(function () {
  'use strict';

  // theme toggle: explicit choice wins over the OS setting, remembered per browser
  var btn = document.getElementById('theme');
  function current() {
    var t = document.documentElement.dataset.theme;
    if (t) return t;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  if (btn) btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) { /* storage blocked: the choice lasts for this page */ }
  });

  // tooltips for every [data-tip]; the first line is the title
  var tip = document.getElementById('tip');
  function show(el) {
    var text = el.getAttribute('data-tip');
    if (!text || !tip) return;
    var lines = text.split('\n');
    var b = document.createElement('b');
    b.textContent = lines[0];
    tip.replaceChildren(b);
    if (lines.length > 1) tip.append('\n' + lines.slice(1).join('\n'));
    tip.hidden = false;
    var r = el.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
    var y = r.bottom + 8;
    if (y + h > window.innerHeight - 8) y = Math.max(8, r.top - h - 8);
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  }
  function hide() { if (tip) tip.hidden = true; }
  document.addEventListener('mouseover', function (e) { var el = e.target.closest('[data-tip]'); if (el) show(el); });
  document.addEventListener('mouseout', function (e) { if (e.target.closest('[data-tip]')) hide(); });
  document.addEventListener('focusin', function (e) { var el = e.target.closest('[data-tip]'); if (el) show(el); });
  document.addEventListener('focusout', hide);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
  window.addEventListener('scroll', hide, true);

  // matrix: highlight the hovered column (rows are CSS :hover)
  document.querySelectorAll('table.matrix').forEach(function (table) {
    // cols[i]: the header and every cell of column i, collected once
    var cols = Array.prototype.map.call(table.querySelectorAll('thead th.col'), function (th) { return [th]; });
    table.querySelectorAll('tbody tr').forEach(function (tr) {
      tr.querySelectorAll('td.cell').forEach(function (td, i) { td.dataset.col = i; if (cols[i]) cols[i].push(td); });
    });
    var last = -1;
    function mark(idx, on) {
      if (idx < 0 || !cols[idx]) return;
      cols[idx].forEach(function (el) { el.classList.toggle('hl', on); });
    }
    table.addEventListener('mouseover', function (e) {
      var td = e.target.closest('td.cell');
      var idx = td ? +td.dataset.col : -1;
      if (idx !== last) { mark(last, false); mark(idx, true); last = idx; }
    });
    table.addEventListener('mouseleave', function () { mark(last, false); last = -1; });
  });

  // component table filter: text plus state chips
  var q = document.getElementById('cfilter'), ctable = document.getElementById('ctable');
  if (q && ctable) {
    var active = {};
    function apply() {
      var s = q.value.trim().toLowerCase(), any = Object.keys(active).length > 0, n = 0;
      ctable.querySelectorAll('tbody tr').forEach(function (tr) {
        var ok = (!s || tr.textContent.toLowerCase().indexOf(s) >= 0) && (!any || active[tr.dataset.state]);
        tr.hidden = !ok;
        if (ok) n++;
      });
      var c = document.getElementById('ccount');
      if (c) c.textContent = n;
    }
    q.addEventListener('input', apply);
    document.querySelectorAll('.fchips button').forEach(function (b) {
      b.addEventListener('click', function () {
        var st = b.dataset.state;
        if (active[st]) delete active[st]; else active[st] = true;
        b.classList.toggle('on', !!active[st]);
        apply();
      });
    });
  }
})();
