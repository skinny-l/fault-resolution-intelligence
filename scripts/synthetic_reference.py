"""
synthetic_reference.py — reference-style entries and the BMC power-fault
error map for the demo knowledge base.

Two things live here:

  REFERENCE_DATA (37 entries) — short lookup-style entries: SEL event
  codes, SMART attributes, accelerator Xid signatures and inter-socket
  link faults. These are deliberately terser than the troubleshooting
  entries in synthetic_entries.py. Real knowledge bases contain both
  shapes, and the mix is what makes BM25 ranking behave realistically:
  if every document were the same length, length normalisation would
  never be exercised.

  POWER_FAULT_ARTICLE — one KB article with a 36-row error map. Each row
  maps a BMC log error pattern to a power rail, suspect components and
  (for memory rails) the DIMM slots that rail feeds. This is what
  fiars.recommend._kb_lookup() matches raw ticket text against.

SMART attribute IDs are real — they are a public de-facto standard and a
technical reader would expect them. Everything else here (rail names,
event codes, Xid numbers, slot labels) is invented.
"""
from __future__ import annotations

SRC_REF = "Demo dataset — SEL/SMART/Xid reference (synthetic)"


def _r(cat, code, desc, parts, cause, fix):
    return {
        "category": cat, "error_code": code, "fault_description": desc,
        "affected_parts": parts, "root_cause": cause, "solution": fix,
        "source": SRC_REF,
    }


# --- BMC SEL event codes (12) ---------------------------------------------
_SEL = [
    _r("Board", "SEL_0x04",
       "SEL event 0x04 — sensor threshold crossed, lower non-critical. The earliest warning the BMC raises for a monitored sensor.",
       "Any monitored sensor",
       "A reading drifting out of its normal band. Informational at this severity.",
       "Identify the sensor from the event, read its current value, and trend it. Act when it reaches critical, not here — unless the drift is fast."),

    _r("Board", "SEL_0x07",
       "SEL event 0x07 — sensor threshold crossed, lower critical. The reading is outside acceptable limits.",
       "Any monitored sensor",
       "A rail, fan or temperature sensor below its critical threshold.",
       "Identify the sensor and treat according to its category. A critical crossing is actionable; correlate with any other events in the same second."),

    _r("Board", "SEL_0x0A",
       "SEL event 0x0A — sensor threshold crossed, upper critical.",
       "Any monitored sensor",
       "A reading above its critical threshold — most often a temperature or a fan running out of range.",
       "Identify the sensor, check the category-specific cause, and correlate against inlet temperature before assuming a node fault."),

    _r("Power", "SEL_0x11",
       "SEL event 0x11 — power supply AC input lost.",
       "SC-PS2000 power supply; PDU outlet; power cord",
       "Loss of AC at the supply inlet. An input-side event, not a supply failure.",
       "Check the PSU input LED, trace the cord to its outlet, and confirm the outlet is live before touching the supply."),

    _r("Power", "SEL_0x14",
       "SEL event 0x14 — power supply predictive failure asserted.",
       "SC-PS2000 power supply",
       "The supply's own monitoring detected degradation ahead of an out-of-spec output.",
       "Verify the peer supply is healthy, then hot-swap the asserting unit. Do not wait for hard failure."),

    _r("Power", "SEL_0x16",
       "SEL event 0x16 — power unit redundancy lost.",
       "SC-PS2000 power supplies; AC feeds",
       "One supply is no longer contributing — failed, removed, or without AC.",
       "Determine which supply and why. Redundancy loss on a single-feed rack means the node is one event away from dropping."),

    _r("Thermal", "SEL_0x1C",
       "SEL event 0x1C — fan sensor below lower non-recoverable threshold.",
       "SC-FN80D fan module",
       "A rotor stopped or slowed past recovery.",
       "Hot-swap the fan module. Confirm both rotors report in range afterwards."),

    _r("Thermal", "SEL_0x1F",
       "SEL event 0x1F — thermal trip, system shut down to protect hardware.",
       "SC-CP9480 processor; heatsink; SC-FN80D fans",
       "A component exceeded its shutdown temperature.",
       "Establish why before powering back on. Check fan health, inlet temperature, baffle fitment and heatsink contact in that order."),

    _r("Memory", "SEL_0x21",
       "SEL event 0x21 — memory correctable ECC error logged with DIMM location.",
       "SC-DR64G RDIMM",
       "A correctable error on the identified module.",
       "Note the location, read per-DIMM counters, and decide on the pattern — one module versus a whole channel."),

    _r("Memory", "SEL_0x23",
       "SEL event 0x23 — memory uncorrectable ECC error with DIMM location.",
       "SC-DR64G RDIMM; memory controller",
       "A hard fault on the identified module, or a controller fault if the pattern is channel-wide.",
       "Record the location before rebooting. Replace the module; escalate to board if errors follow the slot."),

    _r("CPU", "SEL_0x2B",
       "SEL event 0x2B — processor internal error (IERR) asserted, with socket identified.",
       "SC-CP9480 processor",
       "An uncorrectable internal processor error.",
       "Collect the screen capture from the log bundle before rebooting, then reseat and inspect the socket."),

    _r("Firmware", "SEL_0x31",
       "SEL event 0x31 — watchdog timer expired, node reset by the BMC.",
       "CoreBMC watchdog; host OS",
       "The host stopped servicing the watchdog. Points at a hung host, not at failed hardware.",
       "Investigate the host OS. A watchdog reset with no other SEL event is a software problem, not a parts request."),
]


# --- SMART attributes (10) -------------------------------------------------
_SMART = [
    _r("Storage", "SMART_1",
       "SMART attribute 1 — Raw Read Error Rate. Vendor-scaled; only meaningful as a trend against itself.",
       "SC-HD18T SAS drive",
       "Read channel errors, most of which are corrected internally.",
       "Do not act on the raw value. Trend it against the same drive's history; act on attributes 5, 197 and 198."),

    _r("Storage", "SMART_5",
       "SMART attribute 5 — Reallocated Sector Count. Sectors already mapped out to the spare pool.",
       "SC-HD18T SAS drive; SC-NV7T6 NVMe drive",
       "Media defects permanently remapped.",
       "A stable non-zero count is wear. A climbing count is a replacement. Read alongside 197 and 198."),

    _r("Storage", "SMART_9",
       "SMART attribute 9 — Power-On Hours. Cumulative service time.",
       "Any drive",
       "Not a fault indicator. Context for interpreting wear attributes.",
       "Use to judge whether a non-zero wear count is expected for the drive's age. Never a replacement trigger on its own."),

    _r("Storage", "SMART_187",
       "SMART attribute 187 — Reported Uncorrectable Errors. Errors that reached the host.",
       "SC-HD18T SAS drive",
       "Reads the drive could not correct, returned as errors.",
       "Any non-zero value is significant — this data reached the application. Replace and flag affected data."),

    _r("Storage", "SMART_188",
       "SMART attribute 188 — Command Timeout. Commands that did not complete in time.",
       "SC-HD18T SAS drive; SC-BP24N backplane; cabling",
       "A drive struggling internally, or a marginal bus. A climbing count with clean media attributes points at the bus.",
       "Correlate with media attributes. Clean media plus climbing timeouts means check the backplane and cabling, not the drive."),

    _r("Storage", "SMART_194",
       "SMART attribute 194 — Temperature. Current drive temperature.",
       "Any drive",
       "Sustained high temperature accelerates wear and raises error rates.",
       "Check against airflow and blanking panels. A single hot drive in a populated bank points at that bay."),

    _r("Storage", "SMART_197",
       "SMART attribute 197 — Current Pending Sector Count. Sectors awaiting reallocation.",
       "SC-HD18T SAS drive",
       "Sectors that failed a read and have not yet been remapped.",
       "A climbing pending count reliably precedes user-visible errors. Replace rather than watch."),

    _r("Storage", "SMART_198",
       "SMART attribute 198 — Offline Uncorrectable. Sectors the background scan cannot read.",
       "SC-HD18T SAS drive",
       "Media defects found by the drive's own scan before the host hit them.",
       "Treat as pre-failure. Schedule replacement; escalate if the count climbs between reads."),

    _r("Storage", "SMART_199",
       "SMART attribute 199 — UDMA CRC Error Count. Errors on the interface, not the media.",
       "SC-BP24N backplane; drive carrier; cabling",
       "Interface signal integrity — a connector or cable problem. Not a media problem.",
       "This attribute exonerates the media. Reseat the drive, clean the bay connector, and check cabling before replacing the drive."),

    _r("Storage", "SMART_231",
       "SMART attribute 231 — SSD Life Left. Remaining endurance as a percentage.",
       "SC-NV7T6 NVMe drive",
       "Normal NAND wear from accumulated writes.",
       "Plan replacement as the value approaches the site threshold. Not a fault — a capacity planning input."),
]


# --- Accelerator Xid-style signatures (8) ----------------------------------
_XID = [
    _r("GPU", "XID_198",
       "Xid 198 — memory rows pending remap on an accelerator module.",
       "SC-XA400 accelerator module",
       "Rows retired after correctable errors; the remap has not yet been applied.",
       "Drain the node and reset the module to apply the remap. Replace if rows keep being retired afterwards."),

    _r("GPU", "XID_205",
       "Xid 205 — double-bit error in accelerator on-die memory.",
       "SC-XA400 accelerator module",
       "An uncorrectable memory error on the module.",
       "Reset and re-run diagnostics. A recurrence on the same module is conclusive — replace."),

    _r("GPU", "XID_212",
       "Xid 212 — accelerator fell off the PCIe bus.",
       "SC-XA400 accelerator module; SC-RS16X riser; auxiliary power",
       "A module, riser or power delivery failure. All three present identically.",
       "Check for a rail event at the same timestamp first. Then reseat module, riser and power leads, and swap slots to isolate."),

    _r("GPU", "XID_219",
       "Xid 219 — accelerator reset required before the module can be used again.",
       "SC-XA400 accelerator module",
       "The module entered an unrecoverable state and needs a reset to return to service.",
       "Drain workloads, reset the module, confirm it returns healthy. Investigate the preceding error, not the reset itself."),

    _r("GPU", "XID_226",
       "Xid 226 — accelerator watchdog timeout. A workload stopped responding on the module.",
       "SC-XA400 accelerator module; host workload",
       "Often a workload fault rather than a hardware fault.",
       "Correlate against the workload before suspecting hardware. A single module with repeated watchdog events across different workloads is the hardware case."),

    _r("GPU", "XID_233",
       "Xid 233 — uncontained ECC error on accelerator memory.",
       "SC-XA400 accelerator module",
       "An uncorrectable error that could not be contained to one process.",
       "Record the bus ID and error, reset the module, run a memory diagnostic. A repeat on the same module is a replacement."),

    _r("GPU", "XID_241",
       "Xid 241 — inter-module link error between two accelerators.",
       "SC-XA400 accelerator modules; inter-module bridge",
       "A bridge connector or a link fault on one of the two endpoints.",
       "Reseat the bridge at both ends, then swap the bridge before suspecting either module."),

    _r("GPU", "XID_247",
       "Xid 247 — accelerator power brake asserted. Clocks capped by the power subsystem.",
       "SC-XA400 accelerator module; SC-PS2000 power supplies",
       "The node is at its power envelope, or a supply is not contributing.",
       "Check PSU redundancy and load sharing. A node running on one supply will brake its accelerators by design."),
]


# --- Processor and inter-socket link faults (7) ---------------------------
_CPULINK = [
    _r("CPU", "UPI_LINK_TRAIN_FAIL",
       "Inter-socket link fails to train at boot. The node boots single-socket or halts.",
       "SC-CP9480 processors; SC-MB2200 system board",
       "A seating or contact fault at either socket, or board trace damage.",
       "Reseat both processors — the fault can originate at either end — and inspect both sockets before condemning the board."),

    _r("CPU", "UPI_LINK_DEGRADE",
       "Inter-socket link trains at reduced width or speed. Cross-socket memory access is slow.",
       "SC-CP9480 processors; SC-MB2200 system board",
       "Marginal contacts on one socket.",
       "Reseat both processors and re-read the negotiated link parameters. Persistent degradation means board replacement."),

    _r("CPU", "CPU_CORE_DISABLED",
       "Fewer cores present than the processor's rated count. BIOS mapped cores out.",
       "SC-CP9480 processor",
       "Cores disabled after failing built-in self-test, or disabled in BIOS configuration.",
       "Check BIOS core configuration first — a configuration setting is far more common than a genuine core failure. Replace only if BIOS shows cores mapped out by BIST."),

    _r("CPU", "CPU_FREQ_CAPPED",
       "Processor sustains a frequency well below its rated turbo range under load.",
       "SC-CP9480 processor; heatsink; SC-PS2000 power supplies",
       "Thermal or power limiting. Nothing has failed — the processor is protecting itself or the node is at its power envelope.",
       "Read temperature and power draw under load. Thermal limiting points at airflow or heatsink contact; power limiting points at supply redundancy or a BIOS power cap."),

    _r("CPU", "CPU_PRESENCE_MISMATCH",
       "BIOS reports a different processor population than is physically installed.",
       "SC-CP9480 processor; SC-MB2200 socket",
       "A processor not fully seated, or a socket presence-detect fault.",
       "Power down, reseat the missing processor, inspect the socket. If a known-good processor is also not detected in that socket, replace the board."),

    _r("CPU", "CPU_MISMATCH_STEPPING",
       "Processors of different steppings or SKUs installed in the same node. Boot may fail or features may be disabled.",
       "SC-CP9480 processors",
       "Mixed processors. SC platforms require matched pairs.",
       "Read both processors' model and stepping. Replace so both match — do not attempt to run a mixed pair."),

    _r("CPU", "CPU_VR_HOT",
       "Processor voltage regulator over-temperature asserted. The processor throttles or the node shuts down.",
       "SC-MB2200 system board VR; SC-FN80D fans; air baffle",
       "Airflow over the VR area is restricted, or the VR itself is failing.",
       "Check baffle fitment and fan health over the VR area first. A VR running hot with confirmed good airflow means board replacement."),
]

REFERENCE_DATA = _SEL + _SMART + _XID + _CPULINK        # 12 + 10 + 8 + 7 = 37

# The legacy loader scripts/load_sel_smart_xid.py covers only the SEL,
# SMART and Xid portion. It shares a dedup sentinel with the reference
# loader, so whichever runs first wins and the other skips — which is the
# behaviour the two loaders have always had.
SEL_SMART_XID = _SEL + _SMART + _XID                     # 30


# =========================================================================
# BMC power-fault KB article — 36 error patterns
# =========================================================================
def _p(pattern, rail, suspects, slots=None, remark=""):
    row = {"error_pattern": pattern, "power_rail": rail,
           "suspect_components": suspects, "dimm_slots": slots or []}
    if remark:
        row["remark"] = remark
    return row


POWER_FAULT_ARTICLE = {
    "title": "CoreBMC Power Fault Error Map (SC platform family)",
    "scope": "SC-2200R, SC-2400H, SC-4800G, SC-1150S, SC-3300M running CoreBMC 3.x",
    "problem": (
        "A node fails to power on, drops unexpectedly, or logs a rail fault. "
        "The BMC records a rail-specific error pattern in the system event log "
        "and in the autolog bundle. The pattern names the rail that failed, and "
        "the rail determines which components are in scope — which is the "
        "difference between a targeted repair and swapping parts until it stops."
    ),
    "root_cause": (
        "A power rail failing to come up in sequence, or collapsing at runtime. "
        "The failure originates in one of three places: the supply feeding the "
        "rail, the board-mounted regulator producing it, or the component "
        "drawing from it. The rail name narrows this to a handful of candidates. "
        "Memory rails narrow it further, to specific DIMM slots, because each "
        "PVDDQ rail feeds a known set of channels."
    ),
    "solution": (
        "1. Capture the full SEL and the autolog bundle BEFORE removing AC. "
        "Rail events are held in volatile state on some firmware levels and are "
        "lost on power removal.\n"
        "2. Match the logged error pattern against this map to identify the rail "
        "and its suspect components.\n"
        "3. For a memory rail, the map gives the DIMM slots that rail feeds — "
        "reseat or replace within those slots only.\n"
        "4. Remove AC for 60 seconds, then retry power-on at minimum "
        "configuration.\n"
        "5. Add components back in groups, retesting after each, until the fault "
        "reproduces.\n"
        "6. A rail fault that reproduces at minimum configuration is a board or "
        "supply fault, not a component fault."
    ),
    "suggestions": (
        "Do not start by replacing the system board. On this platform family the "
        "majority of rail faults resolve to a single component drawing out of "
        "spec, a partially seated module, or a supply that is not sharing load. "
        "The board is the last candidate, not the first.\n"
        "Check whether both supplies are present, matched and sharing before "
        "investigating any rail — an unbalanced pair produces rail events that "
        "look like component faults.\n"
        "If two or more unrelated rails assert in the same second, suspect the "
        "supply or the sequencer, not the components."
    ),
    "source_url": "",
    "error_map": [
        # --- main rails ---
        _p("RAIL_P12V_MAIN_FAULT", "P12V_MAIN",
           ["SC-PS2000 power supply", "SC-MB2200 system board", "backplane power cabling"],
           remark="Affects everything downstream. Check supply pairing and load sharing before any component work."),
        _p("RAIL_P12V_STBY_FAULT", "P12V_STBY",
           ["SC-PS2000 power supply", "SC-MB2200 system board"],
           remark="Standby rail. A fault here usually means the node will not respond to a power-on request at all."),
        _p("RAIL_P5V_AUX_FAULT", "P5V_AUX",
           ["SC-MB2200 system board", "SC-BP24N backplane"]),
        _p("RAIL_P3V3_AUX_FAULT", "P3V3_AUX",
           ["SC-MB2200 system board", "SC-RS16X riser"]),
        _p("RAIL_P3V_RTC_LOW", "P3V_RTC",
           ["CR2032 RTC cell", "SC-MB2200 system board"],
           remark="Almost always a depleted coin cell. Replace the cell before suspecting the board."),
        _p("RAIL_P1V8_PCH_FAULT", "P1V8_PCH",
           ["SC-MB2200 system board"]),
        _p("RAIL_PVNN_PCH_FAULT", "PVNN_PCH",
           ["SC-MB2200 system board"]),

        # --- processor core rails ---
        _p("RAIL_PVCCIN_CPU0_FAULT", "PVCCIN_CPU0",
           ["SC-CP9480 processor (socket 0)", "SC-MB2200 system board VR"],
           remark="Reseat socket 0 and inspect for bent pins before condemning the board."),
        _p("RAIL_PVCCIN_CPU1_FAULT", "PVCCIN_CPU1",
           ["SC-CP9480 processor (socket 1)", "SC-MB2200 system board VR"],
           remark="Reseat socket 1 and inspect for bent pins before condemning the board."),
        _p("VRHOT_CPU0", "PVCCIN_CPU0",
           ["SC-MB2200 system board VR", "SC-FN80D fan module", "air baffle"],
           remark="Thermal, not electrical. Check airflow over the VR area first."),
        _p("VRHOT_CPU1", "PVCCIN_CPU1",
           ["SC-MB2200 system board VR", "SC-FN80D fan module", "air baffle"],
           remark="Thermal, not electrical. Check airflow over the VR area first."),
        _p("RAIL_PVCCFA_CPU0_FAULT", "PVCCFA_CPU0",
           ["SC-CP9480 processor (socket 0)", "SC-MB2200 system board VR"]),
        _p("RAIL_PVCCFA_CPU1_FAULT", "PVCCFA_CPU1",
           ["SC-CP9480 processor (socket 1)", "SC-MB2200 system board VR"]),

        # --- memory rails (with DIMM slot mapping) ---
        _p("RAIL_PVDDQ_AB_CPU0_FAULT", "PVDDQ_AB_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_A0", "CPU0_B0"],
           remark="Reseat or replace within these slots only. A fault that persists with all four slots empty is board-side."),
        _p("RAIL_PVDDQ_CD_CPU0_FAULT", "PVDDQ_CD_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_C0", "CPU0_D0"]),
        _p("RAIL_PVDDQ_EF_CPU0_FAULT", "PVDDQ_EF_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_E0", "CPU0_F0"]),
        _p("RAIL_PVDDQ_GH_CPU0_FAULT", "PVDDQ_GH_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_G0", "CPU0_H0"]),
        _p("RAIL_PVDDQ_AB_CPU1_FAULT", "PVDDQ_AB_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_A0", "CPU1_B0"]),
        _p("RAIL_PVDDQ_CD_CPU1_FAULT", "PVDDQ_CD_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_C0", "CPU1_D0"]),
        _p("RAIL_PVDDQ_EF_CPU1_FAULT", "PVDDQ_EF_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_E0", "CPU1_F0"]),
        _p("RAIL_PVDDQ_GH_CPU1_FAULT", "PVDDQ_GH_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_G0", "CPU1_H0"]),
        _p("RAIL_PVPP_AB_CPU0_FAULT", "PVPP_AB_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_A0", "CPU0_B0"],
           remark="DIMM activation rail. Presents as a training failure more often than a hard power fault."),
        _p("RAIL_PVPP_CD_CPU0_FAULT", "PVPP_CD_CPU0",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU0_C0", "CPU0_D0"]),
        _p("RAIL_PVPP_AB_CPU1_FAULT", "PVPP_AB_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_A0", "CPU1_B0"]),
        _p("RAIL_PVPP_CD_CPU1_FAULT", "PVPP_CD_CPU1",
           ["SC-DR64G RDIMM", "SC-MB2200 system board VR"],
           ["CPU1_C0", "CPU1_D0"]),

        # --- riser, backplane and adapter rails ---
        _p("RAIL_P12V_RISER1_FAULT", "P12V_RISER1",
           ["SC-RS16X riser", "SC-XA400 accelerator module", "SC-NX200 adapter"],
           remark="Remove everything behind riser 1 and retest before replacing the riser."),
        _p("RAIL_P12V_RISER2_FAULT", "P12V_RISER2",
           ["SC-RS16X riser", "SC-XA400 accelerator module", "SC-NX200 adapter"]),
        _p("RAIL_P12V_BP_FAULT", "P12V_BP",
           ["SC-BP24N backplane", "SC-NV7T6 NVMe drive", "SC-HD18T SAS drive", "backplane power cabling"],
           remark="A single shorted drive can pull this rail down. Depopulate the bank and add drives back in groups."),
        _p("RAIL_P12V_OCP_FAULT", "P12V_OCP",
           ["SC-NX200 OCP adapter", "SC-MB2200 system board"]),
        _p("RAIL_P12V_XA_A_FAULT", "P12V_XA_A",
           ["SC-XA400 accelerator module", "auxiliary power cabling", "SC-RS16X riser"],
           remark="Accelerator auxiliary rail, modules 1-4. Check connector latching before replacing a module."),
        _p("RAIL_P12V_XA_B_FAULT", "P12V_XA_B",
           ["SC-XA400 accelerator module", "auxiliary power cabling", "SC-RS16X riser"],
           remark="Accelerator auxiliary rail, modules 5-8."),

        # --- supply and sequencing events ---
        _p("PSU_OUTPUT_OC_ASSERT", "P12V_MAIN",
           ["SC-PS2000 power supply", "SC-XA400 accelerator module", "SC-MB2200 system board"],
           remark="Real overcurrent is plausible on accelerator nodes. Retest with accelerators removed."),
        _p("PSU_INPUT_LOST", "AC_INPUT",
           ["SC-PS2000 power supply", "PDU outlet", "power cord"],
           remark="Input-side event. Check the outlet before touching the supply."),
        _p("PSU_MISMATCH_DETECTED", "P12V_MAIN",
           ["SC-PS2000 power supply"],
           remark="Mismatched ratings or firmware. SC platforms require matched pairs."),
        _p("PWR_GOOD_TIMEOUT", "SEQUENCER",
           ["SC-MB2200 system board", "SC-PS2000 power supply", "SC-CP9480 processor"],
           remark="The log names the sequence step that stalled — that step names the rail."),
        _p("CPLD_SEQ_ABORT", "SEQUENCER",
           ["CPLD on SC-MB2200", "CoreBMC firmware"],
           remark="Check the firmware set is qualified together before treating this as a hardware fault."),
    ],
}
