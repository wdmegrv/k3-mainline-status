#!/usr/bin/env python3
"""Render the K3 upstream status site.

Reads features/k3.yaml (the feature rows) and socs/<soc>.yaml (the inventory
of each SoC) and renders static HTML into _site/:

    index.html              feature matrix and component matrix: one row per feature / DT component,
                            one column per analysed SoC (a SoC without socs/<soc>.yaml is not shown)
    soc/<soc>.html          one page per SoC: facts, features, the TI patches per feature and component,
                            components, undescribed devices, TI's SDK claims, mailing lists, notes
    assets/                 style.css, app.js

    python3 site/build.py [-o DIR] [--socs DIR]   # default _site/, socs/
    python3 -m http.server -d _site      # preview

Needs PyYAML and Jinja2. The YAML files are the only data; the site holds nothing of its own.
"""
import argparse
import datetime as dt
import html
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

HERE = Path(__file__).resolve().parent
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)  # libyaml is ~8x faster
ROOT = HERE.parent

SOC_ORDER = ["am62x", "am62ax", "am62px", "am67x", "am64x", "am68x", "am62lx"]
GROUP_ORDER = ["Multimedia", "Compute & IPC", "Connectivity", "Storage", "System", "Power"]
DOMAIN_ORDER = ["MCU", "Wakeup", "Main"]

# where a commit of the vendor kernel and of mainline can be read
TI_COMMIT = "https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/commit/?id={sha}"
MAINLINE_COMMIT = "https://git.kernel.org/torvalds/c/{sha}"

# the TI material the inventories are built from ("Sources" on the index page)
TI_KERNEL = "https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/"
TI_TAG = "https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/tag/?h={tag}"
TI_BRANCH = "https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel/log/?h={branch}"
TI_FIRMWARE = "https://git.ti.com/cgit/processor-firmware/ti-linux-firmware/"
TI_FIRMWARE_MIRROR = "https://github.com/TexasInstruments/ti-linux-firmware"
TISCI_DOC = "https://software-dl.ti.com/tisci/esd/latest/5_soc_doc/"
SDK_DOCS = "https://software-dl.ti.com/processor-sdk-linux/esd/{dev}/latest/exports/docs/index.html"
SDK_DOCS_SOURCE = "https://github.com/TexasInstruments/processor-sdk-doc"
# SoCs whose SDK docs are not at SDK_DOCS/<SOC upper case>: the J7-family devices live under jacinto7/
SDK_DOCS_OTHER = {"am67x": "https://software-dl.ti.com/jacinto7/esd/processor-sdk-linux-am67/latest/exports/docs/index.html"}

# state class -> (label, meaning, rank); rank orders "worst wins" when rows merge
STATES = {
    "ok":      ("Mainline",        "merged into torvalds/master", 0),
    "next":    ("Queued",          "picked for -next or a maintainer tree", 2),
    "pending": ("On the list",     "posted, under review", 3),
    "partial": ("Partial",         "in mainline, but nodes, drivers, Kconfig or firmware lag behind, or the driver is upstream without its DT node; vendor patches alone do not count", 4),
    "missing": ("Missing",         "vendor-only or not upstream at all", 5),
    "neutral": ("No gap",          "parent node, firmware-owned, nothing to drive, or mainline is ahead", 1),
    "na":      ("Not on this SoC", "the SoC does not have the block", -1),
    "unknown": ("Not analysed",    "no inventory for this SoC yet", -2),
}
MAIN_STATES = [k for k, v in STATES.items() if v[2] >= 0]  # the states a SoC page counts
STATE_CLASS = {
    "mainline": "ok", "added": "ok", "driver": "ok",
    "next": "next", "pending": "pending",
    "partial": "partial", "node-missing": "partial", "vendor-driver": "partial",
    "vendor-only": "missing", "missing": "missing",
    "no-driver": "neutral", "parent": "neutral", "upstream-only": "neutral", "undescribed": "neutral",
    "n/a": "na", "-": "na", "": "unknown",
}

# patch class (subject prefix of the vendor kernel) -> (label, meaning); the site shows the label, never the key
PATCH_CLASSES = {
    "U": ("Backport", "Subject prefix UPSTREAM or BACKPORT: a copy of a commit that is already in mainline"),
    "F": ("Posted", "Subject prefix FROMLIST: sent to a mailing list, not merged when TI took it"),
    "P": ("Not posted", "Subject prefix PENDING: TI's own work, not sent to a mailing list yet"),
    "H": ("TI only", "Subject prefix TI, HACK or WORKAROUND: kept in TI's kernel, not meant for mainline"),
    "?": ("No prefix", "No subject prefix: TI did not classify it"),
}
PREFIX_RE = re.compile(r"^(?:(?:UPSTREAM|BACKPORT|FROMLIST|PENDING|TI|HACK|WORKAROUND)\s*:\s*)+", re.I)


def state_class(raw):
    return STATE_CLASS.get(raw.strip().lower(), "neutral")


def patch_tally(plist):
    """Counts by class, how many are not upstream (neither a backport nor landed in mainline since) and how many
    non-backports have landed."""
    counts = Counter(p["class"] for p in plist)
    pending = sum(1 for p in plist if p["class"] != "U" and not p["upstream"])
    landed = sum(1 for p in plist if p["class"] != "U" and p["upstream"])
    return counts, pending, landed


def patch_fields(plist, not_upstream=None):
    """The patches of a row with their patch_tally(); the inventory's own not-upstream number wins when it has one."""
    counts, pending, landed = patch_tally(plist)
    return {"patches": plist, "patch_counts": ", ".join(f"{counts[k]} {PATCH_CLASSES[k][0] if PATCH_CLASSES[k][0].startswith('TI') else PATCH_CLASSES[k][0].lower()}" for k in PATCH_CLASSES if counts[k]),
            "patch_pending": int(not_upstream) if not_upstream is not None else pending,
            "patch_landed": landed}


def patch_css(cls):
    """CSS suffix of a patch class: 'pc-U', …, 'pc-X' for the unclassified."""
    return cls if cls in PATCH_CLASSES and cls != "?" else "X"


def patch_text(r):
    """'2 backport, 3 posted, 1 not posted (3 not upstream, 1 landed since)' for a tooltip."""
    if not r["patches"]:
        return ""
    bits = ([f"{r['patch_pending']} not upstream"] if r["patch_pending"] else []) + \
           ([f"{r['patch_landed']} landed since"] if r["patch_landed"] else [])
    return r["patch_counts"] + (f" ({', '.join(bits)})" if bits else "")


def rank(cls):
    return STATES[cls][2]


# ------------------------------------------------------------------- text

URL_RE = re.compile(r"https?://[^\s<>\"']+")
TRAIL = ".,;:!?)'\""


def shorten_url(url):
    u = re.sub(r"^https?://", "", url).rstrip("/")
    return u if len(u) <= 60 else u[:38] + "…" + u[-18:]


def inline(text):
    """Escape, then `code`, **bold**, [text](url) and bare URLs."""
    t = html.escape(text, quote=False)
    links = []

    def keep(m):
        links.append(f'<a href="{m.group(2)}">{m.group(1)}</a>')
        return f"\x00{len(links) - 1}\x00"

    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", keep, t)

    def auto(m):
        url = m.group(0)
        tail = ""
        while url and url[-1] in TRAIL and not (url[-1] == ")" and url.count("(") >= url.count(")")):
            tail = url[-1] + tail
            url = url[:-1]
        return f'<a href="{url}">{shorten_url(url)}</a>{tail}'

    t = URL_RE.sub(auto, t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: links[int(m.group(1))], t)
    return t


def chip(raw):
    cls = state_class(raw)
    return f'<span class="chip st-{cls}"><i></i>{html.escape(raw)}</span>'


def s(v):
    """YAML scalar as text: dates and numbers included, None as ''."""
    return "" if v is None else str(v)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def iso_to_de(v):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s(v))
    return f"{m.group(3)}.{m.group(2)}.{m.group(1)}" if m else s(v)


def soc_display(soc_id):
    m = re.match(r"^am(\d+)([a-z]*)x$", soc_id)
    return f"AM{m.group(1)}{m.group(2).upper()}x" if m else soc_id.upper()


def mainline_version(version):
    """'v7.3-rc6-78-g47324d3a5b3a' -> 'v7.3-rc6'."""
    m = re.match(r"(v\d+(?:\.\d+)*(?:-rc\d+)?)", s(version))
    return m.group(1) if m else ""


# ------------------------------------------------------------------- socs

def component_domain(name, fam):
    if name.startswith("mcu_") or fam.startswith("MCU_"):
        return "MCU"
    if name.startswith("wkup_") or fam.startswith("WKUP_"):
        return "Wakeup"
    return "Main"


def facts_of(d):
    """The header lines of a SoC page from the structured keys and the free `facts` mapping."""
    out = []
    down, up = d.get("down") or {}, d.get("up") or {}
    if d.get("board"):
        v = f"{s(d['board'])} (TI reference board, both refs)"
        if d.get("dtsi"):
            v += f" · SoC dtsi {s(d['dtsi'])}" + (f" ({s(d['includes'])})" if d.get("includes") else "")
        out.append(("Board DT", v))
    if down:
        bits = [f"tip {iso_to_de(down['tip'])}" if down.get("tip") else "", f"base {s(down['base'])}" if down.get("base") else "",
                f"{s(down['commits'])} commits on top" if down.get("commits") else "", f"TI SDK {s(down['sdk'])}" if down.get("sdk") else "",
                f"newest tag {s(down['tag'])}" if down.get("tag") else ""]
        v = s(down.get("ref")) + (" (" + ", ".join(b for b in bits if b) + ")" if any(bits) else "")
        if down.get("cicd"):
            v += f"; the -cicd branch is {s(down['cicd'])} commits ahead"
        out.append(("Vendor kernel", v))
    if up:
        out.append(("Mainline", f"{s(up.get('ref'))} = {s(up.get('version'))}" + (f" ({iso_to_de(up['date'])})" if up.get("date") else "")))
    if d.get("config"):
        cfg = d["config"] if isinstance(d["config"], list) else [d["config"]]
        out.append(("Config", " + ".join(s(c) for c in cfg)))
    for k, v in (d.get("facts") or {}).items():
        out.append((s(k), s(v)))
    if d.get("run"):
        out.append(("Run", iso_to_de(d["run"]) + (f" (previous {iso_to_de(d['previous'])})" if d.get("previous") else "")))
    return out


def load_soc(path, features):
    with open(path, encoding="utf-8") as fh:
        d = yaml.load(fh, Loader=YAML_LOADER) or {}
    sid = s(d.get("soc")) or path.stem
    down, up = d.get("down") or {}, d.get("up") or {}
    soc = {"id": sid, "name": s(d.get("name")) or soc_display(sid), "detail": s(d.get("detail")),
           "run": iso_to_de(d.get("run")), "base": s(down.get("base")), "ref": s(down.get("ref")), "tag": s(down.get("tag")),
           "mainline": mainline_version(up.get("version")), "snapshot": s(up.get("date")), "facts": facts_of(d)}

    patches = {}
    for sha, p in (d.get("patches") or {}).items():
        sha, p = s(sha), p or {}
        cls = s(p.get("class")) or "?"
        patches[sha] = {"sha": sha, "class": cls, "subject": s(p.get("subject")),
                        "title": PREFIX_RE.sub("", s(p.get("subject"))) or s(p.get("subject")),
                        "href": TI_COMMIT.format(sha=sha),
                        "upstream": s(p.get("upstream")), "upstream_href": MAINLINE_COMMIT.format(sha=s(p["upstream"])) if p.get("upstream") else "",
                        "lore": s(p.get("lore"))}

    def plist_of(x):
        return [patches[s(sha)] for sha in x.get("patches") or [] if s(sha) in patches]

    comps, seen = [], Counter()
    for c in d.get("components") or []:
        name, fam, state = s(c.get("name")), s(c.get("family")), s(c.get("state"))
        seen[name] += 1
        comps.append({"name": name, "family": fam, "instances": int(c.get("instances") or 1),
                      "nodes": [s(n) for n in c.get("nodes") or []],
                      "driver": s(c.get("driver")) or "-", "kconfig": s(c.get("kconfig")) or "-", "dt": s(c.get("dt")),
                      "state": state, "cls": state_class(state), "notes": s(c.get("notes")),
                      "domain": component_domain(name, fam),
                      "anchor": "c-" + slug(name) + ("" if seen[name] == 1 else f"-{seen[name]}"),
                      "panchor": "p-c-" + slug(name), **patch_fields(plist_of(c), c.get("not_upstream"))})
    soc["components"] = comps
    soc["components_by_name"] = {}
    for c in comps:
        soc["components_by_name"].setdefault(c["name"], []).append(c)
    soc["components_have"] = {k: any(c[k] for c in comps) for k in ("nodes", "dt", "patches")}
    # entries of one name (several states) share the patches: list them once
    soc["component_patch_rows"] = [cs[0] for cs in soc["components_by_name"].values() if cs[0]["patches"]]

    rows = []
    for f in d.get("features") or []:
        fid = s(f.get("id"))
        fdef = features.get(fid)
        if fdef is None:
            print(f"{path.name}: feature {fid!r} is not in features/k3.yaml", file=sys.stderr)
        state = s(f.get("state"))
        rows.append({"id": fid, "name": fdef["name"] if fdef else fid, "state": state, "cls": state_class(state), "anchor": "f-" + fid,
                     "nodes": s(f.get("nodes")) or "-", "drivers": s(f.get("drivers")) or "-",
                     "kconfig": [s(x) for x in f.get("kconfig") or []], "firmware": s(f.get("firmware")) or "-",
                     "gaps": [s(g) for g in f.get("gaps") or []], "notes": s(f.get("notes")),
                     **patch_fields(plist_of(f), f.get("not_upstream"))})
    soc["feature_rows"] = rows
    soc["feature_by_id"] = {r["id"]: r for r in rows}
    soc["feature_counts"] = Counter(r["cls"] for r in rows)
    soc["component_counts"] = Counter(c["cls"] for c in comps)
    soc["patch_count"] = len(patches)
    soc["patch_counts"], soc["patch_pending"], soc["patch_landed"] = patch_tally(list(patches.values()))
    soc["commits"] = s(down.get("commits"))

    soc["undescribed"] = [{"device": s(x.get("device")), "note": s(x.get("note"))} for x in d.get("undescribed") or []]
    sdk = d.get("sdk") or {}
    soc["sdk"] = {"version": s(sdk.get("version")), "page": s(sdk.get("page")), "date": iso_to_de(sdk.get("date")),
                  "claims": [{"feature": s(c.get("feature")), "upstream": s(c.get("upstream")), "notes": s(c.get("notes"))} for c in sdk.get("claims") or []],
                  "remarks": [s(r) for r in sdk.get("remarks") or []]} if sdk else None
    lists = d.get("lists") or {}
    soc["lists"] = {"date": iso_to_de(lists.get("date")),
                    "series": [{k: s(x.get(k)) for k in ("series", "for", "state", "link")} for x in lists.get("series") or []]} if lists else None
    soc["notes"] = [s(n) for n in d.get("notes") or []]
    return soc


# ----------------------------------------------------------------- matrices

def tip(lines):
    return "\n".join(f"{k}: {v}" if k else v for k, v in lines if v)


def clip(text, n=320):
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def feature_label(f):
    """Row label and what the name adds to it: 'Display: DSS, OLDI, DSI' -> ('Display', 'DSS, OLDI, DSI'),
    'Camera: CSI-2 RX' with short 'CSI-2 RX' -> ('CSI-2 RX', ''), 'Storage: SD / eMMC (SDHCI)' -> ('SD / eMMC', 'SDHCI')."""
    short = f.get("short") or f["name"].split(":")[0]
    name = f["name"]
    sub = name.split(":", 1)[1].strip() if ":" in name else name
    m = re.search(r"(?<!\w)" + re.escape(short) + r"(?!\w)", sub, re.I)
    if m:
        sub = re.sub(r"\s{2,}", " ", (sub[:m.start()] + sub[m.end():]).strip(" :-,+"))
        if sub.startswith("(") and sub.endswith(")") and sub.count("(") == 1:
            sub = sub[1:-1]
    elif sub.lower() in short.lower():
        sub = ""
    return short, sub


def feature_matrix(features, socs, soc_ids):
    """Rows = the features of the yaml by group, columns = the analysed SoCs."""
    groups = {g: [] for g in GROUP_ORDER}
    for fid, f in features.items():
        label, sub = feature_label(f)
        have = [x.lower() for x in f.get("socs", [])]
        cells = []
        for sid in soc_ids:
            soc = socs[sid]
            if sid not in have:
                cells.append({"cls": "na", "text": "–", "tip": f"{soc['name']} has no {f['name']}"})
                continue
            r = soc["feature_by_id"].get(fid)
            if r is None:
                cells.append({"cls": "unknown", "text": "no row", "tip": f"{soc['name']} · {f['name']}\nno row in the inventory"})
                continue
            cells.append({"cls": r["cls"], "text": r["state"] or "?", "href": f"soc/{sid}.html#{r['anchor']}", "n": r["patch_pending"],
                          "tip": tip([("", f"{soc['name']} · {f['name']}"), ("State", r["state"]),
                                      ("Nodes", r["nodes"]), ("Drivers", r["drivers"]),
                                      ("Kconfig", " ".join(r["kconfig"])), ("Firmware", r["firmware"]),
                                      ("Patches", patch_text(r)), ("Gaps", clip("; ".join(r["gaps"]))),
                                      ("Notes", clip(r["notes"]))])})
        groups.setdefault(f.get("group", "Other"), []).append({"id": fid, "label": label, "sub": sub, "cells": cells})
    groups = {g: rows for g, rows in groups.items() if rows}
    return {"groups": groups, "nrows": sum(len(r) for r in groups.values())}


def component_matrix(socs, soc_ids):
    """Rows = the DT components by power domain, columns = the analysed SoCs; a row is the worst of its instances."""
    keys = {d: {} for d in DOMAIN_ORDER}
    for sid in soc_ids:
        for c in socs[sid]["components"]:
            k = keys[c["domain"]].setdefault(c["name"], {"name": c["name"], "families": set()})
            if c["family"]:
                k["families"].add(c["family"])
    groups = {}
    for d, ks in keys.items():
        rows = []
        for name, k in ks.items():
            cells = []
            for sid in soc_ids:
                soc = socs[sid]
                hits = soc["components_by_name"].get(name)
                if not hits:
                    cells.append({"cls": "na", "text": "–", "tip": f"{soc['name']} has no {name} node"})
                    continue
                worst = max(hits, key=lambda c: rank(c["cls"]))
                lines = [("", f"{soc['name']} · {name}" + (f" ({worst['family']})" if worst["family"] else ""))]
                for c in hits:
                    lines.append(("", f"{c['state']}: {c['driver']}, {c['kconfig']}"))
                    if c["nodes"]:
                        lines.append(("", "nodes " + ", ".join(c["nodes"]) + (f" · TI board: {c['dt']}" if c["dt"] else "")))
                    if c["notes"]:
                        lines.append(("", clip(c["notes"], 240)))
                lines.append(("Patches", patch_text(worst)))
                cells.append({"cls": worst["cls"], "text": worst["state"] or "?", "href": f"soc/{sid}.html#{worst['anchor']}",
                              "n": worst["patch_pending"], "tip": tip(lines)})
            rows.append({"id": name, "label": name, "sub": ", ".join(sorted(k["families"])), "cells": cells})
        if rows:
            groups[d] = rows
    return {"groups": groups, "nrows": sum(len(r) for r in groups.values())}


# ------------------------------------------------------------------ sources

def fact_url(soc, key):
    """The first URL in the SoC's fact line `key`, '' if there is none."""
    for k, v in soc["facts"]:
        m = URL_RE.search(v) if k == key else None
        if m:
            return m.group(0).rstrip(TRAIL)
    return ""


def sources(socs, soc_ids):
    """The Sources section of the index page: the vendor kernel the analysis ran on,
    the per-SoC TI documents (one row each, one column per SoC) and the repositories."""
    refs = Counter((socs[sid]["ref"], socs[sid]["tag"]) for sid in soc_ids if socs[sid]["ref"])
    ref, tag = refs.most_common(1)[0][0] if refs else ("", "")
    branch = ref.split("/", 1)[-1]
    kernel = {"ref": branch, "ref_href": TI_BRANCH.format(branch=branch) if branch else "",
              "tag": tag, "tag_href": TI_TAG.format(tag=tag) if tag else "",
              "others": [socs[sid]["name"] for sid in soc_ids if (socs[sid]["ref"], socs[sid]["tag"]) != (ref, tag)]}

    tisci = lambda sid: fact_url(socs[sid], "TISCI")
    upstream = lambda sid: fact_url(socs[sid], "TI SDK upstream status")
    per_soc = [
        {"name": "TISCI device list", "what": "System firmware device ids: the hardware side, joined with the DT nodes to find devices nothing describes.",
         "f": tisci, "label": "devices"},
        {"name": "Processor SDK Linux docs", "what": "Per-device SDK documentation; its kernel-driver pages cross-check the inventory.",
         "f": lambda sid: SDK_DOCS_OTHER.get(sid) or SDK_DOCS.format(dev=sid.upper()), "label": "docs"},
        {"name": "TI upstream status page", "what": "TI's own list of what is upstream; checked in the SDK claims table of a SoC page.",
         "f": upstream, "label": "status"},
    ]
    rows = [{"name": r["name"], "what": r["what"], "cells": [(r["label"], r["f"](sid)) for sid in soc_ids]} for r in per_soc]
    rows = [r for r in rows if any(href for _, href in r["cells"])]

    repos = [
        {"name": "TI kernel", "what": "The vendor side of every row; the patches behind a feature link into it.",
         "links": [("git.ti.com", TI_KERNEL)]},
        {"name": "TI firmware", "what": "ti-dm, ti-ipc, ti-pruss, cnm, powervr, ti-connectivity: the firmware checks of the features.",
         "links": [("git.ti.com", TI_FIRMWARE), ("GitHub mirror", TI_FIRMWARE_MIRROR)]},
        {"name": "processor-sdk-doc", "what": "Source of the SDK docs above.", "links": [("GitHub", SDK_DOCS_SOURCE)]},
    ]
    if not any(r["name"] == "TISCI device list" for r in rows):
        repos.append({"name": "TISCI docs", "what": "System firmware device ids of the K3 SoCs.", "links": [("software-dl.ti.com", TISCI_DOC)]})
    return {"kernel": kernel, "per_soc": rows, "repos": repos}


def vendor_rows(socs, soc_ids):
    """The Vendor patches table of the index page: one row per SoC with its patch totals."""
    out = []
    for sid in soc_ids:
        x = socs[sid]
        out.append({"id": sid, "name": x["name"], "href": f"soc/{sid}.html", "commits": x["commits"], "count": x["patch_count"],
                    "counts": x["patch_counts"], "pending": x["patch_pending"], "landed": x["patch_landed"],
                    "features": sum(1 for r in x["feature_rows"] if r["patch_pending"]),
                    "components": sum(1 for c in x["component_patch_rows"] if c["patch_pending"])})
    return out


# ------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", default=str(ROOT / "_site"), help="output directory (default _site/)")
    ap.add_argument("--repo-url", default="", help="link to the repository shown in the footer")
    ap.add_argument("--socs", default=str(ROOT / "socs"), help="directory of the socs/<soc>.yaml files (default socs/)")
    a = ap.parse_args()
    out = Path(a.out)

    with open(ROOT / "features" / "k3.yaml", encoding="utf-8") as fh:
        features = yaml.load(fh, Loader=YAML_LOADER)
    socs = {}
    for p in sorted(Path(a.socs).glob("*.yaml")):
        soc = load_soc(p, features)
        socs[soc["id"]] = soc

    soc_ids = [x for x in SOC_ORDER if x in socs] + sorted(set(socs) - set(SOC_ORDER))
    if not soc_ids:
        sys.exit(f"no <soc>.yaml in {a.socs} to render")

    snapshots = [(x["snapshot"], x["mainline"]) for x in socs.values() if x.get("mainline")]
    snapshot_date, mainline = max(snapshots) if snapshots else ("", "")
    fm = feature_matrix(features, socs, soc_ids)
    cm = component_matrix(socs, soc_ids)
    src = sources(socs, soc_ids)
    ctx = {
        "soc_ids": soc_ids, "cols": [{"name": socs[sid]["name"], "detail": socs[sid]["detail"], "href": f"soc/{sid}.html"} for sid in soc_ids],
        "fm": fm, "cm": cm, "states": STATES, "main_states": MAIN_STATES, "patch_classes": PATCH_CLASSES,
        "mainline": mainline, "snapshot": iso_to_de(snapshot_date),
        "sources": src, "vendor": vendor_rows(socs, soc_ids),
        "generated": dt.date.today().strftime("%d.%m.%Y"), "repo_url": a.repo_url,
    }

    env = Environment(loader=FileSystemLoader(HERE / "templates"), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["inline"] = lambda t: Markup(inline(t or ""))
    env.filters["chip"] = lambda t: Markup(chip(t or ""))
    env.filters["de"] = iso_to_de
    env.filters["short"] = shorten_url
    env.filters["pc"] = patch_css

    if out.exists():
        shutil.rmtree(out)
    (out / "soc").mkdir(parents=True)
    shutil.copytree(HERE / "assets", out / "assets")
    (out / ".nojekyll").write_text("")

    def render(name, path, **kw):
        path.write_text(env.get_template(name).render(ctx, **kw), encoding="utf-8")

    render("index.html", out / "index.html", root="")
    for sid in soc_ids:
        render("soc.html", out / "soc" / f"{sid}.html", root="../", soc=socs[sid])
    print(f"{out}: index, {len(socs)} SoC pages ({', '.join(soc_ids)}); "
          f"{fm['nrows']} feature rows, {cm['nrows']} component rows × {len(soc_ids)} SoCs; "
          f"{sum(x['patch_count'] for x in socs.values())} patches, {sum(x['patch_pending'] for x in socs.values())} not upstream")


if __name__ == "__main__":
    main()
