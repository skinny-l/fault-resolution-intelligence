"""
generate_synthetic_kb.py — (re)generate the entire demo dataset.

    python -m scripts.generate_synthetic_kb

Writes every file under kb_content/ and samples/. The output is
deterministic: the same seed produces byte-identical files, so the
committed dataset can be verified by regenerating it and diffing.

This script exists so the repository can prove its own claim. The
knowledge base shipped here is not a redacted copy of anything — it is
generated from the authored content in scripts/synthetic_entries.py and
scripts/synthetic_reference.py, describing the fictional hardware
universe defined in scripts/synthetic_spec.py. Delete kb_content/*.json,
run this, and you get the same dataset back.
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import synthetic_spec as spec
from scripts.synthetic_entries import (
    CONFIRMED_SOLUTIONS, SERVER_FAULT_KB, PLATFORM_FAULTS, ACCEL_FAULTS,
)
from scripts.synthetic_reference import (
    REFERENCE_DATA, SEL_SMART_XID, POWER_FAULT_ARTICLE,
)

SEED = 20260921
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(ROOT, "kb_content")
SAMPLES_DIR = os.path.join(ROOT, "samples")

# Anchor date for the generated case history. Fixed, not date.today(), so
# regenerating the dataset next month does not rewrite every file.
ANCHOR = date(2026, 9, 1)

# Deliberately non-name-like. These are placeholders in a demo dataset,
# not people.
ENGINEERS = ["Tech-01", "Tech-02", "Tech-03", "Tech-04", "Tech-05", "Tech-06"]

HALLS = ["Hall-A", "Hall-B", "Hall-C"]

# Short outcome labels. recommend.py aggregates cases into confidence-scored
# buckets by exact label match, so the labels have to repeat across cases for
# the ranking to have anything to rank. Varying which label a given fault
# resolves to is what produces a realistic confidence spread rather than a
# single 100%-confidence answer for every query.
FIX_LABELS = {
    "Storage": [
        ("Replaced drive", 55), ("Reseated drive in bay", 20),
        ("Cleaned bay connector and reseated", 10),
        ("Replaced backplane", 8), ("No fault found on retest", 7),
    ],
    "Memory": [
        ("Replaced DIMM", 50), ("Reseated DIMM", 22),
        ("Corrected DIMM population order", 12),
        ("Replaced system board", 9), ("No fault found on retest", 7),
    ],
    "CPU": [
        ("Reseated processor and reapplied TIM", 38), ("Replaced processor", 30),
        ("Updated BIOS microcode", 16), ("Replaced system board", 10),
        ("No fault found on retest", 6),
    ],
    "GPU": [
        ("Reseated accelerator module and power leads", 34),
        ("Replaced accelerator module", 28), ("Reset module and applied remap", 18),
        ("Replaced riser", 12), ("No fault found on retest", 8),
    ],
    "Power": [
        ("Replaced power supply", 46), ("Reseated power cord at PDU", 24),
        ("Escalated to facilities", 15), ("Replaced system board", 8),
        ("No fault found on retest", 7),
    ],
    "Thermal": [
        ("Replaced fan module", 44), ("Refitted air baffle", 22),
        ("Reseated fan module", 16), ("Escalated to facilities", 11),
        ("No fault found on retest", 7),
    ],
    "Network": [
        ("Cleaned fibre end faces", 30), ("Replaced transceiver", 26),
        ("Replaced patch lead", 16), ("Reseated OCP adapter", 15),
        ("Replaced OCP adapter", 13),
    ],
    "BIOS": [
        ("Reapplied BIOS settings", 34), ("Replaced RTC battery", 26),
        ("Reflashed BIOS", 20), ("Corrected DIMM population order", 12),
        ("Replaced system board", 8),
    ],
    "Firmware": [
        ("Updated firmware to qualified set", 42), ("Cold-reset BMC", 30),
        ("Cleared and exported SEL", 16), ("Replaced system board", 12),
    ],
    "Board": [
        ("Reseated cabling", 32), ("Replaced system board", 26),
        ("Replaced backplane", 18), ("Replaced RTC battery", 14),
        ("No fault found on retest", 10),
    ],
    "System": [
        ("Escalated to facilities", 30), ("Updated firmware to qualified set", 26),
        ("No fault found on retest", 24), ("Replaced system board", 20),
    ],
}

PART_LABELS = {
    "Storage": ["SC-HD18T 18TB SAS", "SC-NV7T6 7.68TB NVMe", "SC-BP24N backplane"],
    "Memory": ["SC-DR64G 64GB DDR5 RDIMM", "SC-MB2200 system board"],
    "CPU": ["SC-CP9480 processor", "SC-MB2200 system board"],
    "GPU": ["SC-XA400 accelerator module", "SC-RS16X riser"],
    "Power": ["SC-PS2000 2000W PSU", "power cord"],
    "Thermal": ["SC-FN80D fan module", "air baffle"],
    "Network": ["SC-NX200 OCP adapter", "optical transceiver", "fibre patch lead"],
    "BIOS": ["CR2032 RTC cell", "SC-MB2200 system board"],
    "Firmware": ["CoreBMC firmware", "BIOS"],
    "Board": ["SC-MB2200 system board", "SC-BP24N backplane", "SC-RS16X riser"],
    "System": ["SC-MB2200 system board"],
}


def _weighted(rng, pairs):
    total = sum(w for _, w in pairs)
    n = rng.randrange(total)
    for label, w in pairs:
        if n < w:
            return label
        n -= w
    return pairs[-1][0]


def _short_cause(entry):
    """First sentence of the entry's root cause, as a bucket label."""
    txt = (entry["root_cause"] or "").strip()
    for sep in (". ", ".\n"):
        if sep in txt:
            txt = txt.split(sep)[0]
            break
    txt = txt.rstrip(".").strip()
    return txt[:110]


def _sn(rng, model):
    """Obviously-synthetic serial. The DEMO infix is deliberate."""
    return f"{model.replace('-', '')}-DEMO-{rng.randrange(10000, 99999)}"


def _location(rng):
    return (f"{rng.choice(HALLS)} / Row-{rng.randrange(1, 13):02d} / "
            f"Rack-{rng.randrange(1, 41):02d} / U{rng.randrange(1, 43):02d}")


def _raw_block(entry, model, product, sn, ticket, when):
    """A synthetic ticket block in the bilingual export shape the parser reads."""
    return (
        "工单标签/tags：demo\n"
        f"工单编号/ticket_number：{ticket}\n"
        f"server_model：{model} server_product：{product}\n"
        f"服务器序列号/server_sn：{sn}\n"
        f"服务器厂商/manufacturer：{spec.OEM}\n"
        f"故障类型/fault_type：{entry['category']}\n"
        f"错误码/error_code：{entry['error_code']}\n"
        f"故障描述/fault_description：{entry['fault_description']}\n"
        f"报障时间/report_time：{when.isoformat()} 09:00:00\n"
    )


def build_cases(n=240):
    """Synthetic resolved-case history for the ranking and pagination demos."""
    rng = random.Random(SEED)
    pool = CONFIRMED_SOLUTIONS + SERVER_FAULT_KB + PLATFORM_FAULTS + ACCEL_FAULTS
    models = list(spec.PLATFORMS.items())
    cases = []

    for i in range(n):
        entry = pool[rng.randrange(len(pool))]
        cat = entry["category"]
        model, (product, _) = models[rng.randrange(len(models))]
        # Cases skew recent, which is what makes the recency term in the
        # ranking visible: older cases exist, but they are outnumbered.
        age = int(abs(rng.gauss(0, 260))) % 730
        when = ANCHOR - timedelta(days=age)
        sn = _sn(rng, model)
        ticket = f"DEMO-{i + 1:05d}"
        recurred = 1 if rng.random() < 0.12 else 0
        fix = _weighted(rng, FIX_LABELS.get(cat, FIX_LABELS["System"]))
        parts = PART_LABELS.get(cat, PART_LABELS["System"])[
            rng.randrange(len(PART_LABELS.get(cat, PART_LABELS["System"])))]

        notes = (
            f"Resolved on site. Outcome: {fix.lower()}."
            + (" Fault recurred within 30 days and was reopened."
               if recurred else "")
        )

        cases.append({
            "ticket_number": ticket,
            "date": when.isoformat(),
            "server_sn": sn,
            "location": _location(rng),
            "error_fault": f"{entry['error_code']} — {entry['fault_description']}",
            "parts": parts,
            "solution": fix,
            "root_cause": _short_cause(entry),
            "recurrence_flag": recurred,
            "engineer": ENGINEERS[rng.randrange(len(ENGINEERS))],
            "notes": notes,
            "resolution_time_min": int(25 + abs(rng.gauss(0, 45))),
            "report_text": "",
            "raw_block": _raw_block(entry, model, product, sn, ticket, when),
        })

    return cases


# =========================================================================
# Sample raw dumps — for the upload / text-extraction / dump-search feature
# =========================================================================
SAMPLE_SEL_CSV = """\
ID,Timestamp,SensorType,SensorName,EventDescription,Severity
1,2026-08-14 02:11:07,Temperature,Inlet_Temp,Upper critical threshold crossed,Critical
2,2026-08-14 02:11:09,Fan,FAN3_R,Lower non-recoverable threshold crossed,Critical
3,2026-08-14 02:11:09,Fan,FAN3_F,Lower critical threshold crossed,Warning
4,2026-08-14 02:12:40,Processor,CPU0_Status,Thermal trip - system shutdown,Critical
5,2026-08-14 02:41:18,System,BMC_Status,System power on,Info
6,2026-08-14 02:41:55,Fan,FAN3_R,Sensor returned to normal range,Info
7,2026-08-19 17:03:22,Memory,DIMM_CPU0_C0,Correctable ECC error,Warning
8,2026-08-19 19:44:51,Memory,DIMM_CPU0_C0,Correctable ECC error,Warning
9,2026-08-20 04:15:02,Memory,DIMM_CPU0_C0,Correctable ECC logging limit reached,Critical
10,2026-08-22 08:30:11,PowerSupply,PSU1_Status,Predictive failure asserted,Warning
"""

SAMPLE_SMART_TXT = """\
smartctl 7.4 — SC-HD18T 18TB SAS 7.2K LFF (demo capture, synthetic)

Device Model:     SC-HD18T
Serial Number:    SCHD18T-DEMO-40117
Firmware Version: SC0142
User Capacity:    18,000,207,937,536 bytes [18.0 TB]
Rotation Rate:    7200 rpm
SMART overall-health self-assessment test result: PASSED

ID# ATTRIBUTE_NAME           VALUE WORST THRESH RAW_VALUE
  1 Raw_Read_Error_Rate        083   074   006   194837221
  5 Reallocated_Sector_Ct      091   091   010   744
  9 Power_On_Hours             058   058   000   37122
187 Reported_Uncorrect         096   096   000   4
188 Command_Timeout            100   100   000   0
194 Temperature_Celsius        031   044   000   38
197 Current_Pending_Sector     088   088   000   162
198 Offline_Uncorrectable      088   088   000   162
199 UDMA_CRC_Error_Count       200   200   000   0

SMART Self-test log:
Num  Test_Description  Status                      LifeTime  LBA_of_first_error
# 1  Extended offline  Completed: read failure      37118     3921004832
# 2  Short offline     Completed without error      37002     -

Note: attributes 5, 197 and 198 are all non-zero and 197 has risen from 41
to 162 over eight days. Overall health still reports PASSED — which is why
the overall verdict is not the deciding signal.
"""

SAMPLE_NVME_TXT = """\
nvme smart-log /dev/nvme3n1 — SC-NV7T6 7.68TB U.2 (demo capture, synthetic)

critical_warning                    : 0x04
temperature                         : 331 K (58 C)
available_spare                     : 12%
available_spare_threshold           : 10%
percentage_used                     : 94%
data_units_read                     : 8,114,927,553
data_units_written                  : 6,002,441,890
host_read_commands                  : 71,220,118,447
host_write_commands                 : 48,902,551,330
controller_busy_time                : 118,442
power_cycles                        : 61
power_on_hours                      : 33,905
unsafe_shutdowns                    : 9
media_errors                        : 2,317
num_err_log_entries                 : 2,402

critical_warning bit 2 set: device reliability degraded.
available_spare is 12%, two points above threshold. media_errors climbing.
"""

SAMPLE_DMESG_LOG = """\
[1842910.442117] SC-XA400: accelerator module 5 (0000:cb:00.0) temperature 89C
[1842910.442199] SC-XA400: module 5 entering thermal slowdown, clocks capped
[1843044.118002] Xid (0000:cb:00.0): 233, uncontained ECC error, channel 6
[1843044.118114] SC-XA400: module 5 marked unhealthy, workload terminated
[1843044.331907] Xid (0000:cb:00.0): 219, reset required before further use
[1843102.550418] pcieport 0000:c9:02.0: AER: Uncorrected (Fatal) error received
[1843102.550522] pcieport 0000:c9:02.0: AER:   device [1d0f:9f42] error status/mask=00100000/00000000
[1843102.550611] Xid (0000:cb:00.0): 212, accelerator has fallen off the bus
[1843102.551204] SC-XA400: module 5 no longer present in enumeration
[1843102.551880] SC-XA400: modules present after fault: 7 of 8

Preceding BMC event, same second:
  RAIL_P12V_XA_B_FAULT asserted, rail P12V_XA_B

Note: the rail event and the Xid 212 share a timestamp. Per the power-fault
error map this is an auxiliary power rail for modules 5-8, so the power path
is the first thing to check, not the module.
"""

SAMPLE_BMC_LOG = """\
CoreBMC 3.4.1 — power fault capture (demo, synthetic)
Platform: SC-2200R / SCR2200-D2-N24
Serial:   SC2200R-DEMO-88214

2026-07-03T22:41:06Z  SEQ  power-on requested via BMC
2026-07-03T22:41:06Z  SEQ  step 1/9  P12V_STBY        OK
2026-07-03T22:41:06Z  SEQ  step 2/9  P5V_AUX          OK
2026-07-03T22:41:06Z  SEQ  step 3/9  P3V3_AUX         OK
2026-07-03T22:41:07Z  SEQ  step 4/9  P12V_MAIN        OK
2026-07-03T22:41:07Z  SEQ  step 5/9  PVCCIN_CPU0      OK
2026-07-03T22:41:07Z  SEQ  step 6/9  PVCCIN_CPU1      OK
2026-07-03T22:41:07Z  SEQ  step 7/9  PVDDQ_AB_CPU0    FAULT
2026-07-03T22:41:07Z  ERR  RAIL_PVDDQ_AB_CPU0_FAULT asserted
2026-07-03T22:41:08Z  ERR  PWR_GOOD_TIMEOUT — sequence aborted at step 7/9
2026-07-03T22:41:08Z  SEQ  returning to standby

PSU status at fault:
  PSU1  present, AC OK, output OK, 412W
  PSU2  present, AC OK, output OK, 408W
  load sharing balanced

Note: PVDDQ_AB_CPU0 feeds DIMM slots CPU0_A0 and CPU0_B0 only.
"""

SAMPLE_EMAIL = """\
From: Dispatch <dispatch@example.invalid>
To: Field Engineering <field@example.invalid>
Subject: [DEMO-00417] Memory fault - SC-2200R - Hall-B Row-04 Rack-22
Date: Thu, 20 Aug 2026 09:14:00 +0800
Content-Type: text/plain; charset=utf-8

工单标签/tags：demo
工单编号/ticket_number：DEMO-00417
server_model：SC-2200R server_product：SCR2200-D2-N24
服务器序列号/server_sn：SC2200R-DEMO-31775
服务器厂商/manufacturer：SynthCore Systems
故障类型/fault_type：Memory
部件类型/part_type：DIMM
部件位置/part_position：CPU0_C0
错误码/error_code：ECC_CE_THRESH
故障描述/fault_description：Correctable ECC error logging limit reached on DIMM_CPU0_C0. Node remains in service. Correctable error count rose from 12 to 4,118 over 36 hours.
报障时间/report_time：2026-08-20 04:15:02
最近30天报修次数/number_of_repairs_in_past_30_days：1
最近60天报修次数/number_of_repairs_in_past_60_days：1

This is a synthetic sample message for the demo dataset. The addresses use
the reserved .invalid TLD and resolve nowhere.
"""

SAMPLE_INVENTORY_CSV = """\
bay,device,model,serial,capacity_tb,link_width,link_speed,health
0,/dev/nvme0n1,SC-NV7T6,SCNV7T6-DEMO-10041,7.68,x4,Gen5,OK
1,/dev/nvme1n1,SC-NV7T6,SCNV7T6-DEMO-10042,7.68,x4,Gen5,OK
2,/dev/nvme2n1,SC-NV7T6,SCNV7T6-DEMO-10043,7.68,x2,Gen5,DEGRADED_LINK
3,/dev/nvme3n1,SC-NV7T6,SCNV7T6-DEMO-10044,7.68,x4,Gen5,MEDIA_ERRORS
4,/dev/nvme4n1,SC-NV7T6,SCNV7T6-DEMO-10045,7.68,x4,Gen5,OK
5,/dev/nvme5n1,SC-NV7T6,SCNV7T6-DEMO-10046,7.68,x4,Gen5,OK
6,,,,,,,ABSENT
7,/dev/nvme7n1,SC-NV7T6,SCNV7T6-DEMO-10048,7.68,x4,Gen5,OK
"""

SAMPLES = {
    "sel_export_demo.csv": SAMPLE_SEL_CSV,
    "smartctl_sas_demo.txt": SAMPLE_SMART_TXT,
    "nvme_smartlog_demo.txt": SAMPLE_NVME_TXT,
    "dmesg_accelerator_demo.log": SAMPLE_DMESG_LOG,
    "bmc_power_fault_demo.log": SAMPLE_BMC_LOG,
    "dispatch_email_demo.eml": SAMPLE_EMAIL,
    "nvme_inventory_demo.csv": SAMPLE_INVENTORY_CSV,
}


def _write_json(name, payload):
    os.makedirs(KB_DIR, exist_ok=True)
    path = os.path.join(KB_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    n = len(payload) if isinstance(payload, list) else len(payload.get("error_map", []))
    print(f"  kb_content/{name}.json  ({n} records)")
    return n


def main():
    print("Generating synthetic demo dataset...")
    total = 0
    total += _write_json("confirmed_solutions", CONFIRMED_SOLUTIONS)
    total += _write_json("server_fault_kb", SERVER_FAULT_KB)
    total += _write_json("platform_faults", PLATFORM_FAULTS)
    total += _write_json("gpu_faults", ACCEL_FAULTS)
    total += _write_json("reference_data", REFERENCE_DATA)
    _write_json("sel_smart_xid", SEL_SMART_XID)
    patterns = _write_json("power_fault_article", POWER_FAULT_ARTICLE)

    cases = build_cases()
    _write_json("demo_cases", cases)

    os.makedirs(SAMPLES_DIR, exist_ok=True)
    for name, body in SAMPLES.items():
        with open(os.path.join(SAMPLES_DIR, name), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(body)
        print(f"  samples/{name}")

    print()
    print(f"  {total} knowledge entries across "
          f"{len(sorted({e['category'] for e in CONFIRMED_SOLUTIONS + SERVER_FAULT_KB + PLATFORM_FAULTS + ACCEL_FAULTS + REFERENCE_DATA}))} categories")
    print(f"  {patterns} BMC error patterns")
    print(f"  {len(cases)} demo cases")
    print(f"  {len(SAMPLES)} sample dump files")
    print("Done. Every identifier above is invented — see scripts/synthetic_spec.py.")


if __name__ == "__main__":
    main()
