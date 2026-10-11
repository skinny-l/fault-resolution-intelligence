"""
synthetic_spec.py — the fictional hardware universe this demo dataset
describes.

Every identifier in here is invented. There is no SynthCore Systems, no
SC-2200R, no CoreBMC. The naming was chosen so that a reader can tell at
a glance that the dataset is fabricated, while the *shape* of the data
(field lengths, code formats, category balance, error-pattern density)
matches what a real fleet knowledge base looks like — which is what the
search ranking, category bias and pagination need in order to behave
realistically.

What is NOT invented, and deliberately so: the open industry standards a
technical reader would expect to see — SMART attribute IDs, IPMI/SEL
terminology, ECC/UCE, MCE, IERR/CATERR, UPI, PCIe AER, Xid as a log
signature class, and public CLI tooling names (ipmitool, smartctl,
nvme-cli, dmidecode, edac-util, nvidia-smi). Those are public
specifications, not anyone's proprietary data. All *values* carried by
those standards in this dataset — the specific Xid numbers, SEL event
codes, rail names, platform SKUs — are fabricated.
"""
from __future__ import annotations

# --- Fictional OEM and platform family ------------------------------------
OEM = "SynthCore Systems"
BMC_FAMILY = "CoreBMC"
LOG_BUNDLE = "autolog"          # fictional one-key log bundle directory

# short model code -> (long product SKU, form factor description)
PLATFORMS = {
    "SC-2200R": ("SCR2200-D2-N24", "2U dual-socket general compute, 24x NVMe"),
    "SC-2400H": ("SCH2400-D2-N48", "2U dual-socket high-density, 48x NVMe"),
    "SC-4800G": ("SCG4800-D2-X8", "4U dual-socket accelerator node, 8x SC-XA400"),
    "SC-1150S": ("SCS1150-S1-N12", "1U single-socket storage, 12x LFF SAS"),
    "SC-3300M": ("SCM3300-D4-M32", "3U quad-socket memory-dense, 32x DDR5 DIMM"),
}

# Fictional field-replaceable units
PARTS = {
    "accelerator": "SC-XA400 accelerator module",
    "nic": "SC-NX200 dual-port 200G OCP 3.0 adapter",
    "psu": "SC-PS2000 2000W CRPS power supply",
    "hdd": "SC-HD18T 18TB SAS 7.2K LFF drive",
    "ssd": "SC-NV7T6 7.68TB U.2 NVMe drive",
    "dimm": "SC-DR64G 64GB DDR5-5600 RDIMM",
    "cpu": "SC-CP9480 48-core processor",
    "fan": "SC-FN80D 80mm dual-rotor fan module",
    "backplane": "SC-BP24N 24-bay NVMe backplane",
    "riser": "SC-RS16X x16 PCIe riser",
    "raid": "SC-RC940 12Gb/s RAID controller",
    "board": "SC-MB2200 system board",
}

# The ten fault categories the knowledge base is partitioned across.
CATEGORIES = [
    "Storage", "Memory", "CPU", "GPU", "Power",
    "Thermal", "Network", "BIOS", "Firmware", "Board",
]

# Fictional power-rail names used by the BMC error map.
RAILS = [
    "P12V_MAIN", "P12V_STBY", "PVCCIN_CPU0", "PVCCIN_CPU1",
    "PVDDQ_AB_CPU0", "PVDDQ_CD_CPU0", "PVDDQ_AB_CPU1", "PVDDQ_CD_CPU1",
    "P5V_AUX", "P3V3_AUX", "P3V_RTC", "P1V8_PCH", "PVNN_PCH",
    "P12V_RISER1", "P12V_RISER2", "P12V_BP",
]

# Fictional DIMM slot labels (channel/slot notation is a generic convention).
DIMM_SLOTS = [f"CPU{c}_{ch}{s}" for c in (0, 1) for ch in "ABCDEFGH" for s in (0,)]
