# k3-mainline-status

Mainline support status of TI K3 SoCs: per SoC, every IP block and feature
(PRU, GPU, VPU, low power, …) with its state in mainline against TI's
vendor kernel.

Site: https://wdmegrv.github.io/k3-mainline-status/

    socs/<soc>.yaml      per-SoC data
    features/k3.yaml     feature definitions
    site/                site generator

    python3 site/build.py    # -> _site/ (pip install -r requirements.txt)
    make serve               # same, then http://localhost:8000/
