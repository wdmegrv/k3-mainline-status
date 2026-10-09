# AM62x (TI K3, AM625)

- Board DT: k3-am625-sk.dts (TI SK, both refs) · SoC dtsi k3-am625.dtsi (k3-am62.dtsi, k3-am62-main/-mcu/-wakeup/-thermal.dtsi)
- Down: ti/ti-linux-6.18.y (tip 2026-10-08, base v6.18.51, TI SDK 12.01 docs, branch tags up to 12.02.00.01; ti-linux-6.18.y-cicd at the same commit) · Up: origin/master = v7.3-rc6-232-gaf32da41b0327 (2026-10-09)
- Config: arch/arm64/configs/defconfig + kernel/configs/ti_arm64_prune.config (TI SDK: make defconfig ti_arm64_prune.config)
- TISCI: https://software-dl.ti.com/tisci/esd/latest/5_soc_doc/am62x/devices.html (150 devices, 90 with a node by id)
- TI SDK upstream status: https://software-dl.ti.com/processor-sdk-linux/esd/AM62X/latest/exports/docs/linux/Foundational_Components/Power_Management/pm_upstream.html (12.01.00.05, page last changed 2026-07-28); the only such page in the AM62X docs
- TI SDK docs: processor-sdk-doc 12.01.00.05.03 (clone 2026-10-06): 31 kernel-driver pages in the AM62X TOC, all mapped to a row; MCRC64 (page 30.11.2024) and K3 DDR (09.12.2025) describe drivers that exist only in ti-linux-6.12.y
- Last run: 2026-10-09 (previous –)

## Components (DT nodes)

One row per block type and state (×N = instances); drivers, Kconfig and states compare ti/ti-linux-6.18.y with origin/master. Node names, compatibles and the DT status of the SK are in the run's TSV, not here.

| Component | Driver | Kconfig | State | Notes |
|---|---|---|---|---|
| mcu_pmx | pinctrl/pinctrl-single.c +1 | PINCTRL_SINGLE=y | mainline |  |
| mcu_esm | - | - | no-driver | no ESM driver on either side |
| mcu_timer ×4 (MCU_TIMER) | clocksource/timer-ti-dm.c | OMAP_DM_TIMER=- | mainline |  |
| mcu_uart (MCU_UART) | tty/serial/8250/8250_early.c +1 | SERIAL_8250_CONSOLE=y SERIAL_8250_OMAP=y | mainline |  |
| mcu_i2c (MCU_I2C) | i2c/busses/i2c-omap.c | I2C_OMAP=y | mainline |  |
| mcu_spi ×2 (MCU_MCSPI) | spi/spi-omap2-mcspi.c | SPI_OMAP24XX=m | mainline |  |
| mcu_gpio_intr (WKUP_MCU_GPIOMUX_INTROUTER) | irqchip/irq-ti-sci-intr.c | TI_SCI_INTR_IRQCHIP=y | mainline |  |
| mcu_gpio (MCU_GPIO) | gpio/gpio-davinci.c | GPIO_DAVINCI=y | mainline |  |
| mcu_rti (MCU_RTI) | watchdog/rti_wdt.c | K3_RTI_WATCHDOG=m | mainline |  |
| mcu_mcan ×2 (MCU_MCAN) | net/can/m_can/m_can_platform.c | CAN_M_CAN_PLATFORM=m | mainline |  |
| mcu_m4fss (MCU_M4FSS0_CORE) | remoteproc/ti_k3_m4_remoteproc.c | TI_K3_M4_REMOTEPROC=m | mainline | power-domains property for M4FSS posted 22.09.2026, under review by Andrew Davis (07.10.2026, https://lore.kernel.org/all/20260922171942.201947-1-sid9.karanam@gmail.com/); firmware am62-mcu-m4f0_0-fw in ti-linux-firmware |
| chipid | soc/ti/k3-socinfo.c | TI_K3_SOCINFO=- | mainline |  |
| opp_efuse_table | generic (syscon) | - | mainline |  |
| cpsw_mac_syscon | generic (syscon) | - | mainline |  |
| usb_phy_ctrl ×2 | generic (syscon) | - | mainline |  |
| target-module (WKUP_UART) | bus/ti-sysc.c | TI_SYSC=- | mainline |  |
| wkup_uart | tty/serial/8250/8250_early.c +1 | SERIAL_8250_CONSOLE=y SERIAL_8250_OMAP=y | mainline |  |
| wkup_i2c (WKUP_I2C) | i2c/busses/i2c-omap.c | I2C_OMAP=y | mainline |  |
| wkup_rtc (WKUP_RTCSS) | rtc/rtc-ti-k3.c | RTC_DRV_TI_K3=m | mainline |  |
| wkup_rti (WKUP_RTI) | watchdog/rti_wdt.c | K3_RTI_WATCHDOG=m | mainline |  |
| wkup_r5fss (WKUP_R5FSS) | remoteproc/ti_k3_r5_remoteproc.c | TI_K3_R5_REMOTEPROC=m | mainline |  |
| wkup_r5fss_core (WKUP_R5FSS0_CORE) | - | - | parent |  |
| wkup_vtm (WKUP_VTM) | thermal/k3_j72xx_bandgap.c | K3_THERMAL=m | mainline |  |
| phy_gmii_sel | phy/ti/phy-gmii-sel.c | PHY_TI_GMII_SEL=- | mainline |  |
| epwm_tbclk | clk/keystone/syscon-clk.c | TI_SYSCON_CLK=- | mainline |  |
| audio_refclk ×2 (BOARD) | clk/keystone/syscon-clk.c | TI_SYSCON_CLK=- | mainline |  |
| dss_oldi_io_ctrl | generic (syscon) | - | mainline | Tomi Valkeinen's Control Module syscon series (28.05.2026, open) renames the node to dss-oldi-io-ctrl; cosmetics |
| dss_clk_ctrl | generic (syscon) | - | node-missing | TI SDK OLDI clock glue (tidss selects the DSS clock through this syscon); mainline describes the OLDI clock as the fixed-factor divider dss_vp1_clk in k3-am62.dtsi and the OLDI bridge (tidss, v6.17) needs no syscon - not an item |
| secure_proxy_main | mailbox/ti-msgmgr.c | TI_MESSAGE_MANAGER=- | mainline |  |
| inta_main_dmss (DMASS0_INTAGGR) | irqchip/irq-ti-sci-inta.c | TI_SCI_INTA_IRQCHIP=y | mainline |  |
| main_bcdma (DMASS0_BCDMA) | dma/ti/k3-udma.c | TI_K3_UDMA=y | mainline |  |
| main_pktdma (DMASS0_PKTDMA) | dma/ti/k3-udma.c | TI_K3_UDMA=y | mainline |  |
| dmsc | firmware/ti_sci.c | TI_SCI_PROTOCOL=- | mainline |  |
| k3_pds | pmdomain/ti/ti_sci_pm_domains.c | TI_SCI_PM_DOMAINS=y | mainline |  |
| k3_clks | clk/keystone/sci-clk.c | TI_SCI_CLK=y | mainline |  |
| k3_reset | reset/reset-ti-sci.c | RESET_TI_SCI=y | mainline |  |
| crypto | crypto/sa2ul.c | CRYPTO_DEV_SA2UL=m | mainline |  |
| rng | char/hw_random/omap-rng.c | HW_RANDOM_OMAP=- | mainline |  |
| secure_proxy_sa | mailbox/ti-msgmgr.c | TI_MESSAGE_MANAGER=- | mainline |  |
| main_pmx | pinctrl/pinctrl-single.c +1 | PINCTRL_SINGLE=y | mainline |  |
| main_esm | - | - | no-driver | no ESM driver on either side |
| main_timer ×8 (TIMER) | clocksource/timer-ti-dm.c | OMAP_DM_TIMER=- | mainline |  |
| main_uart ×7 (UART) | tty/serial/8250/8250_early.c +1 | SERIAL_8250_CONSOLE=y SERIAL_8250_OMAP=y | mainline |  |
| main_i2c ×4 (I2C) | i2c/busses/i2c-omap.c | I2C_OMAP=y | mainline |  |
| main_spi ×3 (MCSPI) | spi/spi-omap2-mcspi.c | SPI_OMAP24XX=m | mainline |  |
| main_gpio_intr (MAIN_GPIOMUX_INTROUTER) | irqchip/irq-ti-sci-intr.c | TI_SCI_INTR_IRQCHIP=y | mainline |  |
| main_gpio ×2 (GPIO) | gpio/gpio-davinci.c | GPIO_DAVINCI=y | mainline |  |
| sdhci ×3 (MMCSD) | mmc/host/sdhci_am654.c | MMC_SDHCI_AM654=y | mainline |  |
| usbss ×2 (MAIN_USB0_ISO_VD) | usb/dwc3/dwc3-am62.c | USB_DWC3_AM62=- | mainline |  |
| usb ×2 | usb/dwc3/core.c +6 | USB_DWC3=y | mainline |  |
| fsas (FSS0_FSAS) | memory/ti-k3-fsas.c (vendor) | TI_K3_FSS_FSAS=y | vendor-only | memory: ti-k3-fsas v2 29.06.2026 open with review comments (Krzysztof Kozlowski, Rob Herring, until 08.07.2026), no v3, not in -next (https://lore.kernel.org/all/20260629072055.896322-1-s-k6@ti.com/) |
| ospi (FSS0_OSPI) | spi/spi-cadence-quadspi.c | SPI_CADENCE_QUADSPI=y | mainline |  |
| gpu (GPU) | gpu/drm/imagination/pvr_drv.c | DRM_POWERVR=m | mainline | AXE-1-16M: driver DRM_POWERVR since v6.8, node mainline, firmware rogue_33.15.11.3 in linux-firmware and ti-linux-firmware |
| cpsw3g (CPSW) | net/ethernet/ti/am65-cpsw-nuss.c | TI_K3_AM65_CPSW_NUSS=y | mainline |  |
| cpsw3g_mdio (CPSW) | net/ethernet/ti/davinci_mdio.c | TI_DAVINCI_MDIO=- | mainline |  |
| cpts (CPSW) | net/ethernet/ti/am65-cpts.c | TI_K3_AM65_CPTS=y | mainline |  |
| dss (DSS) | gpu/drm/tidss/tidss_drv.c | DRM_TIDSS=m | mainline | OLDI bridge in tidss since v6.17, oldi0/oldi1 nodes in mainline k3-am62-main.dtsi; OLDI panel overlays for AM625-SK (Microtips SK-LCD1) and BeaglePlay (LincolnTech LCD-185) in v7.3-rc1; TI's tidss fixes are in the prep series v1 03.09.2026, see Display |
| timesync_router | mux/ti-k3-event-mux.c (vendor) | MUX_TI_K3_EVENT_ROUTER=m | vendor-only | event mux router v1 28.08.2026, binding discussion with Conor Dooley and Peter Rosin until 19.09.2026, no v2 (https://lore.kernel.org/all/20260828100615.1700223-1-r-sharma3@ti.com/); node disabled on the SK |
| hwspinlock | hwspinlock/omap_hwspinlock.c | HWSPINLOCK_OMAP=m | mainline |  |
| mailbox_cluster | mailbox/omap-mailbox.c | OMAP2PLUS_MBOX=m | mainline |  |
| ecap ×3 (ECAP) | pwm/pwm-tiecap.c | PWM_TIECAP=m | mainline |  |
| eqep ×3 (EQEP) | counter/ti-eqep.c | TI_EQEP=m | mainline |  |
| main_mcan (MCAN) | net/can/m_can/m_can_platform.c | CAN_M_CAN_PLATFORM=m | mainline |  |
| main_rti ×5 (RTI) | watchdog/rti_wdt.c | K3_RTI_WATCHDOG=m | mainline |  |
| epwm ×3 (EPWM) | pwm/pwm-tiehrpwm.c | PWM_TIEHRPWM=m | mainline |  |
| mcasp ×3 (MCASP) | sound/soc/ti/davinci-mcasp.c | SND_SOC_DAVINCI_MCASP=m | mainline |  |
| ti_csi2rx (CSI_RX_IF) | media/platform/ti/j721e-csi2rx/j721e-csi2rx.c | VIDEO_TI_J721E_CSI2RX=m | mainline |  |
| cdns_csi2rx (CSI_RX_IF) | media/platform/cadence/cdns-csi2rx.c | VIDEO_CADENCE_CSI2RX=m | mainline |  |
| dphy (DPHY_RX) | phy/cadence/cdns-dphy-rx.c | PHY_CADENCE_DPHY_RX=m | mainline |  |
| pruss (ICSSM) | soc/ti/pruss.c | TI_PRUSS=m | mainline |  |
| pruss_cfg | generic (syscon) | - | mainline |  |
| pruss_intc | irqchip/irq-pruss-intc.c | TI_PRUSS_INTC=- | mainline |  |
| pruss_uart (ICSSM) | tty/serial/8250/8250_pruss.c (vendor) | SERIAL_8250_PRUSS=m | vendor-only | serial: 8250: PRUSS UART v1 13.05.2025 got review comments (Greg KH, Andy Shevchenko, Krzysztof Kozlowski), no v2 since (https://lore.kernel.org/all/20250513215934.933807-1-jm@ti.com/); node disabled on the SK, TI builds SERIAL_8250_PRUSS=m |
| pru ×2 | remoteproc/pru_rproc.c | PRU_REMOTEPROC=- | mainline |  |
| gpmc (GPMC) | memory/omap-gpmc.c | OMAP_GPMC=m | mainline | disabled on the SK |
| elm (ELM) | mtd/nand/raw/omap_elm.c | MTD_NAND_OMAP_BCH_BUILD=- | mainline | disabled on the SK |
| a53_opp_table | - | - | no-driver | served by ti-cpufreq through the SoC compatible; not a gap. TI's ti,soc-info OPP property and k3-socinfo device link (v2 01.04.2026) not applied, only the EPROBE_DEFER patch of that series landed (v7.2) |

## Features

Patches = TI patches on top of v6.18.51 touching the feature, by prefix: U upstream, F FROMLIST, P PENDING, H TI/HACK. Kconfig marks are from TI's SDK config (defconfig + ti_arm64_prune.config); ~SYM = symbol only in the TI kernel.

| Feature | Nodes | Drivers | Kconfig | Firmware | Patches | State | Gaps | Notes |
|---|---|---|---|---|---|---|---|---|
| Display: DSS, OLDI, DSI | 4: 3 mainline, 1 node-missing | 2/2 up | DRM_TIDSS=m DRM_CDNS_DSI_J721E=- | - | F11 P7 H2 | partial | dss_clk_ctrl node-missing; 20 patches not upstream | AM62x: one DSS, two OLDI TXes; AM62Px/AM67x: DSS0+DSS1, OLDI, DSI; AM62Ax: DPI only; AM62x OLDI is mainline (tidss OLDI bridge v6.17, oldi0/oldi1 nodes, dss_vp1_clk divider); of the 20 TI patches one landed (vblank time, v6.19), the FROMLIST ones (OLDI polarities, DPIENABLE, DPI detect, i2097, sampling edge, dispc_is_idle, display sharing) are in Tomi Valkeinen's prep series v1 03.09.2026, open, reviewed/tested by TI (https://lore.kernel.org/all/20260903-tidss-pre-beagley-v1-0-93928baa8b12@ideasonboard.com/) and the BeagleY-AI series v3 29.05.2026 (AM62P DSS, not AM62x); 7 PENDING and 2 HACK are TI-only (ALWAYS_ON_DISPLAY and SELF_REFRESH properties, splash screen, crtc timings, PM domains on probe, DPI0_CLK_CTRL fix, errata log level); dss_clk_ctrl is SDK glue, see Components |
| GPU: PowerVR Rogue (AXE / BXS) | 1: 1 mainline | 1/1 up | DRM_POWERVR=m | ok | 0 | mainline |  | driver state says nothing about GLES/Vulkan conformance - keep the graphics section of the report; AXE-1-16M: DRM_POWERVR since v6.8, node mainline, firmware rogue_33.15.11.3 in linux-firmware; TI's build guide: open-source stack available for AXE-1-16M, Vulkan via Mesa pvr, GL 2.1 via Zink (experimental, not mainline Mesa) |
| Camera: CSI-2 RX | 2: 2 mainline | 2/2 up | VIDEO_TI_J721E_CSI2RX=m VIDEO_CADENCE_CSI2RX=m | - | F16 P9 H1 | partial | 26 patches not upstream | AM67x: four CSI-2 RX instances; the 26 TI patches are mostly stale: runtime PM, system suspend and the multistream rework landed in v7.2, RAW12 bayer formats are in linux-next since 11.09.2026 (v7.4); TI-only: metadata formats, 10-bit GREY, RAW10 RGBIr, DMA init at probe (PENDING, not posted) and the drain HACK; DT gap: mainline k3-am62-main.dtsi gives the CSI2RX shim one BCDMA channel (rx0), TI's dtsi four (rx0-rx3), and the multi-stream DT series v3 23.09.2026 adds the channels for AM62P/J722S/J7 only, not for AM62x (https://lore.kernel.org/all/20260923093459.28125-1-y-abhilashchandra@ti.com/) |
| MCU M4F remoteproc | 1: 1 mainline | 1/1 up | TI_K3_M4_REMOTEPROC=m | ok | F1 P5 | partial | 6 patches not upstream | graceful shutdown v2 25.11.2025 open, discussed until 21.01.2026 (Mathieu Poirier, Patrick Oppenlander), no v3 (https://lore.kernel.org/all/20251125083746.2605721-1-b-padhi@ti.com/); suspend/resume, PM QoS handler, IPC-only ops override and MCU-initiated system shutdown (08.10.2026) are TI PENDING, not posted; TI's upstream page: without them mainline needs rmmod ti_k3_m4_remoteproc before suspend; firmware am62-mcu-m4f0_0-fw in ti-linux-firmware (ti-ipc) |
| Device manager: wakeup R5F (DM firmware) | 2: 1 mainline, 1 parent | 1/1 up | TI_K3_R5_REMOTEPROC=m | missing: am62-wkup-r5f0_0-fw | - | partial | firmware am62-wkup-r5f0_0-fw missing | the DM firmware is loaded by U-Boot; Linux needs the node for IPC and low power; the firmware-name is the BSP's name for ti-dm/am62xx/ipc_echo_testb_mcu1_0_release_strip.xer5f; no AM62x DM series pending (IO+DDR is AM62A/AM62P only) |
| IPC: mailboxes, rpmsg, hwspinlock | 4: 4 mainline | 5/5 up | OMAP2PLUS_MBOX=m TI_MESSAGE_MANAGER=- HWSPINLOCK_OMAP=m RPMSG_VIRTIO=y RPMSG_CHAR=m RPMSG_CTRL=m | ok | P2 H1 | partial | 3 patches not upstream | 3 minor TI patches (mailbox ifdef cleanup, remoteproc suspend order, rpmsg char endpoint HACK), not posted |
| PRU-ICSS (ICSSM): cores, INTC, UART | 6: 5 mainline, 1 vendor-only | 3/4 up | TI_PRUSS=m PRU_REMOTEPROC=- TI_PRUSS_INTC=- ~SERIAL_8250_PRUSS=m | missing: am62x-pru0-fw am62x-pru1-fw | F4 P3 | partial | pruss_uart vendor-only; 8250_pruss.c vendor-only; SERIAL_8250_PRUSS vendor-only; firmware am62x-pru0-fw missing; firmware am62x-pru1-fw missing; 7 patches not upstream | no ICSSM Ethernet nodes for AM62x in the TI kernel either; PRU firmware is application specific (no am62x-pru*-fw in ti-linux-firmware); PRU UART driver v1 13.05.2025 stalled after review (see Components); irq-pruss-intc fixes v2 18.02.2026 (Meghana Malladi) not in mainline or -next (https://lore.kernel.org/all/20260218093730.3123342-2-m-malladi@ti.com/); PRU IPC-only mode and virtio rpmsg are TI PENDING, not posted |
| Ethernet: CPSW3G, CPTS/PTP | 4: 4 mainline | 3/3 up | TI_K3_AM65_CPSW_NUSS=y TI_K3_AM65_CPTS=y PHY_TI_GMII_SEL=- | - | U3 F12 P37 H2 | partial | 51 patches not upstream | base function, PTP and TSN are mainline; most of the 51 TI patches are not AM62x: the CPSW proxy client (30+ PENDING, AM64x EthFw) and cut-thru (AM64x); AF_XDP zero copy v2 09.11.2025 (Roger Quadros) open, no v3 (https://lore.kernel.org/all/20251109-am65-cpsw-xdp-zc-v2-0-858f60a09d12@kernel.org/); flow classification and ALE policer save/restore carry FROMLIST but were not found on lore (?); ALE multicast fix landed v7.0; PENDING fixes (IRQ affinity, Rx teardown descriptor leak, port lookup) not posted |
| USB 2.0: DWC3 | 6: 6 mainline | 1/1 up | USB_DWC3_AM62=- | - | 0 | mainline |  |  |
| Storage: SD / eMMC (SDHCI) | 3: 3 mainline | 1/1 up | MMC_SDHCI_AM654=y | - | P7 | partial | 7 patches not upstream | 7 TI PENDING patches (DLL defaults and FRQSEL, DDR52 limited to 40 MHz on AM62, POWER_ON polling, J721e OTAP), not posted |
| Storage: OSPI / QSPI NOR (FSS) | 3: 2 mainline, 1 vendor-only | 1/2 up | SPI_CADENCE_QUADSPI=y MTD_SPI_NOR=y ~TI_K3_FSS_FSAS=y | - | F5 P4 | partial | fsas0 vendor-only; ti-k3-fsas.c vendor-only; TI_K3_FSS_FSAS vendor-only; 9 patches not upstream | ti-k3-fsas (FSAS error handling) is TI-only; fsas driver v2 29.06.2026 open (see Components); cadence-quadspi PHY tuning / DQS series v10 29.09.2026 open (Santhosh Kumar K, https://lore.kernel.org/all/20260929063529.1235417-1-s-k6@ti.com/); 3 PENDING quadspi patches (DMA EPROBE_DEFER, DTR/PHY on chip-select switch, PHY restore after resume) not posted |
| Storage: GPMC NAND + ELM | 2: 2 mainline | 3/3 up | OMAP_GPMC=m MTD_NAND_OMAP2=m MTD_NAND_OMAP_BCH=y | - | 0 | mainline |  | AM62Ax/AM62Px/AM67x: TISCI knows GPMC0/ELM0 but neither kernel has a node; AM62x: gpmc0/elm0 nodes mainline, disabled on the SK |
| Security: SA3UL/SA2UL crypto, RNG, OP-TEE | 3: 3 mainline | 3/3 up | CRYPTO_DEV_SA2UL=m HW_RANDOM_OMAP=- OPTEE=y | - | 0 | mainline |  |  |
| MCRC64: 64-bit CRC engine | - | 0/1 up | ?CRYPTO_DEV_TI_MCRC64=- | - | 0 | undescribed | MCU_MCRC64_0 undescribed; MCRC64_0 undescribed; mcrc64.c absent; CRYPTO_DEV_TI_MCRC64 unknown | TI SDK docs still list the driver; it exists only in ti-linux-6.6.y/6.12.y (node crc@30300000, ti,am62-mcrc64), dropped from 6.18; upstream v3 30.05.2024 rejected (no in-kernel user for crc64-iso3309, https://lore.kernel.org/all/20240524-mcrc64-upstream-v3-0-24b94d8e8578@ti.com/); TI's 09.2024 reply announced MCRC (crc8/16/32) drivers instead, none posted |
| CAN: MCAN | 3: 3 mainline | 1/1 up | CAN_M_CAN_PLATFORM=m | - | U1 | mainline |  | CAN wakeup from low power (ti,am62-mcan compatible, m_can out-of-band wakeup v8 01.10.2026 and DT v3 12.09.2026) is open, see Low power |
| Audio: McASP | 3: 3 mainline | 1/1 up | SND_SOC_DAVINCI_MCASP=m | - | F8 | partial | 8 patches not upstream | all 8 FROMLIST patches landed (asynchronous mode, pdir, ifdef cleanup v7.0; system suspend/resume, aux_div, auxclk helper v7.1; audio-graph-card2 v7.2): effectively mainline, TI prefixes stale |
| PWM / eCAP / eQEP | 10: 10 mainline | 3/3 up | PWM_TIEHRPWM=m PWM_TIECAP=m TI_EQEP=m | - | U1 | mainline |  |  |
| Watchdog: RTI | 7: 7 mainline | 1/1 up | K3_RTI_WATCHDOG=m | - | F1 | partial | 1 patches not upstream | the one FROMLIST patch (reaction control) landed v7.2: effectively mainline |
| RTC (wakeup domain) | 1: 1 mainline | 1/1 up | RTC_DRV_TI_K3=m | - | P15 H1 | partial | 16 patches not upstream | most downstream RTC patches are low-power wakeup work; 'resume from IO DDR low power mode' v2 13.03.2026 landed v7.1 (AUTOSEL to stable) despite the PENDING prefix; the other 14 (GPIO chip for external wakeup pins, power-off prepare, pre-configured RTC cleanup, AM62L bits) not posted |
| Thermal (VTM) and cpufreq | 3: 2 mainline, 1 no-driver | 2/2 up | K3_THERMAL=m ARM_TI_CPUFREQ=- | - | U1 P2 | partial | 2 patches not upstream | AM64x has no OPP table (fixed frequency); the a53_opp_table no-driver flag is ti-cpufreq, fine; cpufreq probe ordering v2 01.04.2026: EPROBE_DEFER landed v7.2, k3-socinfo device link and ti,soc-info OPP property not applied (https://lore.kernel.org/all/20260401105404.1194717-1-a-kaur@ti.com/) |
| DDR subsystem: temperature monitoring, refresh derating, PMU | - | 0/4 up | ?TI_K3_DDR=- ?K3_DDR_TEMP=- ?MFD_TI_DDRSS=- | - | 0 | undescribed | DDR16SS0 undescribed; k3-ddr.c absent; ti-ddrss-mr4.c absent; ti-ddrss-core.c absent; ti_k3_ddr_perf.c absent; TI_K3_DDR unknown; K3_DDR_TEMP unknown; MFD_TI_DDRSS unknown | TI SDK docs claim DDR temperature monitoring; the k3-ddr driver and the ti,am62a-ddrss node exist only in ti-linux-6.12.y, dropped from 6.18; upstream RFC 14.07.2026 (MFD + MR4 refresh + PMU, AM62P node) NAKed on the bindings, no v2 (https://lore.kernel.org/all/20260714125532.3304178-1-v-mannuru@ti.com/); AM62x: DDR16SS0 (16-bit LPDDR4/DDR4); without it the DRAM keeps the refresh rate the firmware sets at boot |
| DMA: BCDMA / PKTDMA, PSI-L | 4: 4 mainline | 3/3 up | TI_K3_UDMA=y TI_K3_UDMA_GLUE_LAYER=y TI_K3_RINGACC=- | - | F16 P3 H1 | partial | 20 patches not upstream | k3-udma-v2 (AM62L) is TI-only; the 16 FROMLIST patches are that k3-udma-v2 refactor series, v12 07.10.2026 open (https://lore.kernel.org/all/20261007102936.2402427-1-s-adivi@ti.com/) - touches the shared k3-udma code, no AM62x function; 3 PENDING fixes ('Fix sporadic crash on AM62x', BCDMA cyclic transfers, TR descriptor size) and a glue HACK not found on lore |
| TI-SCI: system firmware interface, PM domains, clocks, IRQ routers | 7: 7 mainline | 6/6 up | TI_SCI_PROTOCOL=- TI_SCI_PM_DOMAINS=y TI_SCI_CLK=y RESET_TI_SCI=y TI_SCI_INTA_IRQCHIP=y TI_SCI_INTR_IRQCHIP=y | - | U4 F5 P3 H1 ?2 | partial | 11 patches not upstream | IRQ and clock context restore, sci-clk restore_context, BOARDCFG_MANAGED and 'don't cache clock rate' landed v7.2, per-line interrupt types v7.0, Partial-IO v6.19; left: bulk device-state API (2 unprefixed), inta IRQ affinity and lazy aggregation, sci-clk SSC (PENDING, not posted), gpio-davinci early context restore HACK |
| GPIO and pinctrl (incl. padconf wakeup IRQs) | 5: 5 mainline | 2/2 up | GPIO_DAVINCI=y PINCTRL_SINGLE=y | - | F1 H2 | partial | 3 patches not upstream | the TI padconf wakeup-interrupt extension (ti,am654-padconf + interrupt-controller) is TI-only; ti,am62l-padconf compatible landed v7.1; the padconf wake-up configuration for AM62 (pinctrl-single + DT) stays a TI HACK; Main GPIO wakeup not upstream, matches TI's table |
| Timesync event router | 1: 1 vendor-only | 1/2 up | MUX_MMIO=y ~MUX_TI_K3_EVENT_ROUTER=m | - | - | partial | timesync_router vendor-only; TIMESYNC_EVENT_ROUTER0 undescribed; ti-k3-event-mux.c vendor-only; MUX_TI_K3_EVENT_ROUTER vendor-only | mainline AM64x describes it as pinctrl-single; TI's ti,am62l-event-mux-router driver is TI-only; pending v1 28.08.2026, binding discussion (see Components); node disabled on the SK |
| Low power: Deep Sleep, MCU-only, Standby, Partial-IO | 6: 4 no-driver, 2 mainline | 4/5 up | SUSPEND=- CPU_IDLE=- ARM_PSCI_CPUIDLE=y ~TI_K3_WKUP_SRC_NOTIFY=m | ok | U21 F10 P17 H10 | partial | WKUP_DEEPSLEEP_SOURCES0 undescribed; k3-wkup-src-notify.c vendor-only; TI_K3_WKUP_SRC_NOTIFY vendor-only; 37 patches not upstream | the modes themselves live in TF-A and the DM firmware; the kernel side is the per-driver suspend/resume stack - read the patch list, not the DT. AM67x and AM64x: no idle states in the TI kernel; TI 12.01 table for AM62x: DeepSleep, MCU-only, Partial-IO, DFS, Runtime PM upstream (DeepSleep and MCU-only with the M4F caveat: remoteproc graceful shutdown and suspend are not upstream, rmmod ti_k3_m4_remoteproc before suspend), Standby not, no IO+DDR on AM62x; wake sources RTC, WKUP GPIO, USB, WKUP UART, MCU IPC upstream, Main UART yes (k3-am62x-sk-common, v7.1), Main GPIO no (TI HACK), CAN daisy chain only for Partial-IO; trees: standby idle-state DT v1 20.08.2026 open, discussed with Nishanth Menon until 11.09.2026 (https://lore.kernel.org/all/20260820-upstream-standby-v1-0-6a0553b9713d@ti.com/) although TI's page (28.07.2026) says no series is pending for AM62x; m_can out-of-band wakeup v8 01.10.2026 (https://lore.kernel.org/all/20261001-temp-v8-0-489dd82e4b50@ti.com/) and ti,am62-mcan DT v3 12.09.2026 (https://lore.kernel.org/all/20260912-smth-v3-0-6fa661ae5a4c@ti.com/) open; pmdomain resume-latency constraints v6 24.09.2026 open (https://lore.kernel.org/all/20260924-topic-lpm-pmdomain-device-constraints-v6-0-a69a4856252b@baylibre.com/); wakeup-source-notify driver (TI builds it =m), 14 rtc-ti-k3 patches, remoteproc suspend/resume and the Main/MCU GPIO wakeup-source DT are TI-only, not posted; the out-of-band wakeup core, Partial-IO and m_can WoL/pinctrl wakeup carry UPSTREAM prefixes and are in; CPU_IDLE has no explicit line in TI's config, ARM_PSCI_CPUIDLE=y selects it |
| WiFi/Bluetooth: CC33xx (M.2 CC3351 module) | - | 0/2 up | ~CC33XX=m ~BT_TI=- | ok | F16 P2 H2 | vendor-only | cc33xx vendor-only; btti_main.c vendor-only; CC33XX vendor-only; BT_TI vendor-only; 20 patches not upstream | module on the carrier board, tracked at SoC scope in the report; TI out-of-tree driver with a series on lore; v5 07.11.2024 was the last cc33xx series (https://lore.kernel.org/all/20241107125209.1736277-1-michael.nemanov@ti.com/), no v6 since; the btti Bluetooth driver was never posted; TI's 12.01 driver matches cc33xx SDK 1.0.2.10 |
| DMA-BUF carveout and SRAM heaps (Edge AI, display sharing) | - | 0/2 up | ~DMABUF_HEAPS_CARVEOUT=y ~SRAM_DMA_HEAP=y | - | - | vendor-only | carveout-heap.c vendor-only; sram-dma-heap.c vendor-only; DMABUF_HEAPS_CARVEOUT vendor-only; SRAM_DMA_HEAP vendor-only | TI-only; enabled in phytec_ti_defconfig; TI's SDK config builds both; no series on lore |
| Safety: ESM error signaling | 2: 2 no-driver | - | - | - | - | partial | WKUP_ESM0 undescribed | nodes on both sides, no driver on either side (firmware / safety MCU territory); WKUP_ESM0 undescribed; no driver anywhere |

## Undescribed TISCI devices

- AM62X_DEV_CMP_EVENT_INTROUTER0 (1): compare-event interrupt router (timer compare events); no node in any K3 dtsi on either side, no Linux consumer - fine
- AM62X_DEV_DMASS0_RINGACC_0 (33): ring accelerator, unused with BCDMA/PKTDMA - fine
- AM62X_DEV_WKUP_GTC0 (61), AM62X_DEV_WKUP_ESM0 (64): firmware territory - fine
- AM62X_DEV_LED0 (83): unknown block, no node anywhere (?)
- AM62X_DEV_MCU_MCRC64_0 (100), AM62X_DEV_MCRC64_0 (116): 64-bit CRC engines; TI's 6.6/6.12 kernels had a driver and a node (crc@30300000), 6.18 and mainline have neither - see the MCRC64 feature row
- AM62X_DEV_WKUP_TIMER0/1 (110/111): no wakeup-domain timer nodes on either side; TI's wakeup-sources page lists WKUP_TIMER0/1 as wakeup source IDs, nothing on lore (?)
- AM62X_DEV_DDR16SS0 (170): the 16-bit DDR subsystem; TI's 6.12 kernel had the k3-ddr temperature driver and a node, 6.18 and mainline have neither - see the DDR subsystem feature row
- AM62X_DEV_HSM0 (225): HSM M4F, firmware-owned; TI's HSM M4F DT series (v3 14.01.2026) and the U-Boot HSM boot series (v7 22.09.2026) cover AM62P/J722S/J721S2/J784S4, not AM62x - fine

## TI SDK 12.01 upstream status (power management page, last changed 28.07.2026)

| Feature | Upstream (TI) | Notes |
|---|---|---|
| DeepSleep | yes | remoteproc graceful shutdown is not upstream (v2 25.11.2025 open); TI's workaround on mainline: rmmod ti_k3_m4_remoteproc before suspend |
| MCU Only | yes | same remoteproc limitation |
| Partial I/O | yes | |
| Dynamic Frequency Scaling | yes | |
| Standby | no | DT idle-state series v1 20.08.2026 open, not on TI's page yet |
| Runtime PM | yes | |
| Wakeup RTC, MCU (WKUP) GPIO, USB, WKUP UART | yes (DeepSleep, MCU Only) | |
| Wakeup Main I/O daisy chain | partial | Main UART yes (k3-am62x-sk-common in v7.1), Main GPIO no (TI HACK in pinctrl-single) |
| Wakeup MCU IPC | MCU Only | |
| Wakeup CAN I/O daisy chain | Partial I/O only | m_can out-of-band wakeup v8 01.10.2026, DT v3 12.09.2026, both open |
| Pending series | none listed for AM62x | the trees say otherwise, see above |

Docs cross-check (processor-sdk-doc clone 2026-10-06): of the 31 kernel-driver pages TI builds for AM62X, two describe drivers no 6.18 kernel has - MCRC64 (CRYPTO_DEV_TI_MCRC64, page last changed 30.11.2024) and K3 DDR (CONFIG_K3_DDR_TEMP, 09.12.2025); both drivers live in ti-linux-6.12.y only. The TSN pages (EST, CBS, IET, tuning) map to the Ethernet row, the PRU-ICSS pages to the PRU row (the pruss-uart page, 14.05.2026, documents the TI-only driver), "IPC for AM62x" to the IPC row, the power-management pages to the low-power, RTC and thermal rows, the graphics pages to the GPU and Display rows. NETCONF/YANG, UBIFS, Jailhouse, SELinux, fTPM, PQC, OP-TEE/ATF and the ML runtimes are not SoC components. The wakeup-sources page marks WKUP I/O daisy chain and RTC I/O as not applicable for AM62x and lists WKUP_I2C0 and WKUP_TIMER0/1 among the wakeup source IDs (WKUP_TIMER0/1 undescribed).

Other TI pages with upstream statements: Graphics build guide (open-source stack available for the AXE-1-16M core: kernel module upstream, firmware in linux-firmware, Vulkan via Mesa, GL 2.1 via Zink, Zink not mainline and experimental); the CPUIdle page describes Standby as the WFI C-state through cpuidle.

## Mailing lists (09.10.2026)

| Series | For | State | Link |
|---|---|---|---|
| drm/tidss: Preparation for AM62P and BeagleY-AI display support v1 | display | open, reviewed/tested by TI (03.09.2026) | https://lore.kernel.org/all/20260903-tidss-pre-beagley-v1-0-93928baa8b12@ideasonboard.com/ |
| BeagleY-AI display v3 (AM62P DSS, OLDI aux driver) | display | superseded by the prep series, repost expected | https://lore.kernel.org/all/20260529-beagley-ai-display-v3-12-7fefdc5d1adf@ideasonboard.com/ |
| arm64: ti: Use syscon for the Control Module (6 patches) | DT cosmetics (dss-oldi-io-ctrl rename) | open (28.05.2026), binding comments, no v2 | https://lore.kernel.org/all/20260528-ti-main-conf-v1-0-a54ac5c8d081@ideasonboard.com/ |
| arm64: dts: ti: add standby cpu idle state to AM62 SoCs v1 | low power (Standby) | open (20.08.2026), discussed until 11.09.2026, no v2 | https://lore.kernel.org/all/20260820-upstream-standby-v1-0-6a0553b9713d@ti.com/ |
| arm64: dts: ti: use ti,am62-mcan compatible for m_can devices v3 | low power (CAN wake) | open (12.09.2026), bot replies only; v1 20.08.2026 (out-band-wakeup property) and v2 02.09.2026 superseded | https://lore.kernel.org/all/20260912-smth-v3-0-6fa661ae5a4c@ti.com/ |
| can: m_can: introduce ti,am62-mcan compatible for out-of-band wakeup v8 | low power (CAN wake) | open (01.10.2026) | https://lore.kernel.org/all/20261001-temp-v8-0-489dd82e4b50@ti.com/ |
| PM: QoS/pmdomains: support resume latencies for system-wide PM v6 | low power | open (24.09.2026) | https://lore.kernel.org/all/20260924-topic-lpm-pmdomain-device-constraints-v6-0-a69a4856252b@baylibre.com/ |
| arm64: dts: ti: k3-am62-mcu: Add power-domains property for M4FSS | M4F | open (22.09.2026), review by Andrew Davis 07.10.2026 | https://lore.kernel.org/all/20260922171942.201947-1-sid9.karanam@gmail.com/ |
| remoteproc: k3: support for graceful shutdown of remote cores v2 | M4F, low power | open since 25.11.2025, discussion ended 21.01.2026, no v3 | https://lore.kernel.org/all/20251125083746.2605721-1-b-padhi@ti.com/ |
| memory: ti-k3-fsas: Add TI FSS_FSAS driver v2 | OSPI | open since 29.06.2026, review comments 08.07.2026, no v3, not in -next | https://lore.kernel.org/all/20260629072055.896322-1-s-k6@ti.com/ |
| spi: cadence-quadspi: add PHY tuning support v10 (19 patches) | OSPI | open (29.09.2026) | https://lore.kernel.org/all/20260929063529.1235417-1-s-k6@ti.com/ |
| Add TI's event mux router driver and build | timesync | open (28.08.2026), binding discussion until 19.09.2026 | https://lore.kernel.org/all/20260828100615.1700223-1-r-sharma3@ti.com/ |
| Introduce PRU UART driver (serial: 8250: Add PRUSS UART driver) | PRU | stalled after review 16.05.2025, no v2 | https://lore.kernel.org/all/20250513215934.933807-1-jm@ti.com/ |
| irqchip/irq-pruss-intc: fixes v2 (3 patches) | PRU | open (18.02.2026), not in -next | https://lore.kernel.org/all/20260218093730.3123342-2-m-malladi@ti.com/ |
| net: ethernet: ti: am65-cpsw: add AF_XDP zero copy support v2 | Ethernet | open since 09.11.2025, no v3 | https://lore.kernel.org/all/20251109-am65-cpsw-xdp-zc-v2-0-858f60a09d12@kernel.org/ |
| dmaengine: ti: k3-udma-v2 (AM62L BCDMA/PKTDMA V2) v12 | DMA | open (07.10.2026) | https://lore.kernel.org/all/20261007102936.2402427-1-s-adivi@ti.com/ |
| media: csi2rx: Support RAW12 bayer formats (2 patches) | camera | applied, linux-next 11.09.2026 (v7.4) | https://lore.kernel.org/all/20260625151756.221096-1-y-abhilashchandra@ti.com/ |
| Add DT support for CSI2RX multi-stream v3 (18 patches) | camera | open (23.09.2026), no replies; covers AM62P/J722S/J7, not AM62x | https://lore.kernel.org/all/20260923093459.28125-1-y-abhilashchandra@ti.com/ |
| cpufreq: ti: Fix probe ordering and add device link support for K3 SoCs v2 | thermal / cpufreq | partially applied: EPROBE_DEFER in v7.2; soc-info binding, device link and DT open, no v3 | https://lore.kernel.org/all/20260401105404.1194717-1-a-kaur@ti.com/ |
| wifi: cc33xx v5 (17 patches) | WiFi | last version 07.11.2024, no v6 | https://lore.kernel.org/all/20241107125209.1736277-1-michael.nemanov@ti.com/ |
| Add support for MCRC64 engine to calculate 64-bit CRC in Full-CPU mode v3 | MCRC64 | rejected (13.09.2024): no in-kernel user for crc64-iso3309; no v4 | https://lore.kernel.org/all/20240524-mcrc64-upstream-v3-0-24b94d8e8578@ti.com/ |
| Add TI K3 DDR subsystem drivers and DT bindings (RFC, 22 patches) | DDR subsystem | open (14.07.2026): bindings NAKed, no v2 | https://lore.kernel.org/all/20260714125532.3304178-1-v-mannuru@ti.com/ |

Landed in mainline since the TI 6.18 branch point (TI prefixes stale): tidss OLDI bridge (v6.17), tidss vblank time (v6.19), ti_sci Partial-IO (v6.19), ti-sci-intr per-line interrupt types and am65-cpsw ALE multicast fix (v7.0), davinci-mcasp asynchronous mode, pdir and ifdef cleanup (v7.0), davinci-mcasp system suspend/resume and aux_div (v7.1), pinctrl ti,am62l-padconf (v7.1), k3-am62x-sk-common Main UART wakeup (v7.1), rtc-ti-k3 IO DDR resume (v7.1), ti_sci IRQ/clock context restore, sci-clk restore_context, BOARDCFG_MANAGED and clk-keystone rate caching (v7.2), j721e-csi2rx runtime PM, system suspend and multistream (v7.2), davinci-mcasp audio-graph-card2 (v7.2), rti_wdt reaction control (v7.2), cpufreq ti EPROBE_DEFER (v7.2).
