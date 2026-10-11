"""
synthetic_entries.py — authored content for the demo knowledge base.

107 knowledge entries across ten fault categories, plus the 36-pattern
BMC power-fault error map. All hardware names, error-code values, rail
names and remediation procedures are invented; see synthetic_spec.py for
the reasoning about what is fabricated and what is retained as public
industry standard.

Entry shape (matches fiars.db.add_knowledge):
    category, error_code, fault_description, affected_parts,
    root_cause, solution, source
"""
from __future__ import annotations

SRC_CONFIRMED = "Demo dataset — confirmed solutions (synthetic)"
SRC_FAULT_KB = "Demo dataset — general fault KB (synthetic)"
SRC_PLATFORM = "Demo dataset — SC platform notes (synthetic)"
SRC_ACCEL = "Demo dataset — accelerator fault codes (synthetic)"
SRC_REF = "Demo dataset — SEL/SMART/Xid reference (synthetic)"


def _e(cat, code, desc, parts, cause, fix, source):
    return {
        "category": cat, "error_code": code, "fault_description": desc,
        "affected_parts": parts, "root_cause": cause, "solution": fix,
        "source": source,
    }


# =========================================================================
# 1. CONFIRMED SOLUTIONS (17) — faults with a verified, repeatable fix
# =========================================================================
CONFIRMED_SOLUTIONS = [
    _e("Thermal", "FAN_TACH_LOW",
       "BMC reports fan tachometer below the lower non-recoverable threshold on one rotor of a dual-rotor module. Chassis fans ramp to 100% and an amber health LED lights.",
       "SC-FN80D 80mm dual-rotor fan module",
       "Rotor bearing wear or a seized rotor. On dual-rotor modules the surviving rotor keeps airflow within limits, so the system stays up and the fault presents as a threshold crossing rather than a thermal event.",
       "1. Confirm the failing rotor with `ipmitool sensor list | grep -i fan` and note which of FAN1_R/FAN1_F is reading low.\n"
       "2. Fan modules are hot-swappable on all SC platforms — no shutdown required.\n"
       "3. Release the latch, extract the module, seat the replacement until the latch clicks.\n"
       "4. Wait 60s for the BMC to re-read the sensor, then confirm both rotors report within range.\n"
       "5. Clear the SEL entry and verify the health LED returns to green.",
       SRC_CONFIRMED),

    _e("Thermal", "FAN_REDUNDANCY_LOST",
       "Fan redundancy lost event asserted in the SEL with no individual fan below threshold. Airflow is sufficient but the N+1 margin is gone.",
       "SC-FN80D fan module; SC-MB2200 system board fan connector",
       "Usually a fan module that has lost BMC presence detect rather than a mechanical failure — a partially seated module or an oxidised connector. A genuine board-side connector fault is the less common cause.",
       "1. Reseat each fan module in turn, checking `ipmitool sdr list | grep -i fan` for presence after each.\n"
       "2. If presence returns after reseating, the module was under-seated — monitor for 24h.\n"
       "3. If one slot never reports presence with a known-good module, the fault is board-side; escalate for system board replacement.\n"
       "4. Do not replace fan modules speculatively — this fault is a presence problem far more often than a mechanical one.",
       SRC_CONFIRMED),

    _e("Power", "PSU_PREDICTIVE_FAIL",
       "One PSU asserts predictive failure. Output is still within spec and the system is carrying load normally on both supplies.",
       "SC-PS2000 2000W CRPS power supply",
       "Internal fan degradation or an ageing output capacitor bank detected by the PSU's own monitoring before output drifts out of spec.",
       "1. Identify the asserting slot: `ipmitool sdr list | grep -i psu`.\n"
       "2. Verify the peer PSU is healthy and carrying load before touching anything — a predictive-fail PSU is still supplying power.\n"
       "3. Confirm both AC feeds are live; pulling a good PSU on a single-feed rack drops the node.\n"
       "4. Hot-swap the asserting PSU. CRPS units are hot-pluggable on all SC platforms.\n"
       "5. Confirm the new unit reports present and sharing load, then clear the SEL.",
       SRC_CONFIRMED),

    _e("Power", "PSU_AC_LOST",
       "PSU reports AC input lost. The node stays up on the surviving supply; a second AC loss would drop it.",
       "SC-PS2000 power supply; rack PDU outlet; C13/C14 power cord",
       "Upstream: a tripped PDU outlet, a dislodged cord, or a failed PDU branch. The PSU itself is usually healthy — this is an input-side event, not a supply failure.",
       "1. Check the PSU input LED before anything else. Dark means no AC present; amber means the supply itself faulted.\n"
       "2. Trace the cord to its PDU outlet and confirm the outlet is energised and not tripped.\n"
       "3. Reseat the cord at both ends.\n"
       "4. If the outlet is dead, this is a facilities issue — hand off rather than replacing the PSU.\n"
       "5. Replace the PSU only if AC is confirmed present at the inlet and the supply still reports input lost.",
       SRC_CONFIRMED),

    _e("Board", "MB_VR_FAULT",
       "Voltage regulator fault asserted on a board-mounted rail. The node either fails to power on or drops under load.",
       "SC-MB2200 system board; SC-CP9480 processor",
       "A failed VR phase on the system board, or a processor drawing outside its expected envelope and tripping the regulator's protection.",
       "1. Capture the full SEL and the failing rail name before power-cycling — the event is lost after AC removal on some firmware levels.\n"
       "2. Remove AC for 60s, then retry power-on with the minimum configuration (one CPU, one DIMM per channel).\n"
       "3. If minimum config powers on, add components back in groups to isolate.\n"
       "4. If a PVCCIN rail is implicated, reseat that processor and inspect the socket for bent pins under good light.\n"
       "5. Socket damage or a repeating rail fault at minimum config means system board replacement.",
       SRC_CONFIRMED),

    _e("Board", "BP_PRESENCE_LOST",
       "Backplane presence lost. An entire bank of drive bays disappears at once from both the OS and the BMC.",
       "SC-BP24N 24-bay NVMe backplane; backplane power and sideband cabling",
       "A dislodged backplane power or sideband cable, or a failed backplane. A whole bank vanishing at once points at the backplane, not at the drives.",
       "1. A whole bank going dark is a backplane symptom — do not start pulling drives.\n"
       "2. Power the node down. Backplane cabling is not a hot-swap operation.\n"
       "3. Reseat the backplane power and sideband connectors at both the backplane and board ends.\n"
       "4. Power on and confirm the bank enumerates.\n"
       "5. If the bank is still missing with cabling confirmed good, replace the backplane.",
       SRC_CONFIRMED),

    _e("CPU", "CPU_IERR",
       "Internal error asserted by a processor. The node halts immediately and the BMC captures a screen image at the point of failure.",
       "SC-CP9480 processor; SC-MB2200 system board socket",
       "An uncorrectable internal processor error. Most often the processor itself; occasionally a socket seating or contact problem presenting as an internal fault.",
       "1. Collect the full log bundle including the IERR screen capture before rebooting — that capture is the primary evidence and does not survive a reboot.\n"
       "2. Note which socket asserted from the SEL entry.\n"
       "3. Power down, reseat the implicated processor, inspect the socket for bent or contaminated pins.\n"
       "4. Reapply thermal interface material and retorque the heatsink to the documented pattern.\n"
       "5. If IERR recurs after a clean reseat, replace the processor. If it follows the socket rather than the processor, replace the board.",
       SRC_CONFIRMED),

    _e("CPU", "CPU_CATERR",
       "Catastrophic error signal asserted. The node halts hard, usually with no OS-side log entry.",
       "SC-CP9480 processor; SC-MB2200 system board",
       "A processor or chipset-level fatal condition. Can also be triggered by a marginal VR rail rather than by the processor itself.",
       "1. Capture the SEL and the CATERR screen image before any power cycle.\n"
       "2. Check whether a VR or rail fault was logged in the same second — if so, treat this as a power fault, not a CPU fault.\n"
       "3. With no rail event, reseat the processor and retest.\n"
       "4. Update BIOS and BMC firmware to the current qualified level; several CATERR signatures are firmware-addressable.\n"
       "5. Replace the processor if CATERR recurs on the same socket after reseat and firmware update.",
       SRC_CONFIRMED),

    _e("Memory", "ECC_CE_THRESH",
       "Correctable ECC error rate on one DIMM crosses the logging threshold. The node stays up and the OS continues to correct.",
       "SC-DR64G 64GB DDR5-5600 RDIMM; DIMM slot contacts",
       "A degrading memory device, or a marginal slot contact. Correctable errors clustering on one DIMM point at the module; errors spread across a whole channel point at the slot or the controller.",
       "1. Read the per-DIMM counters: `edac-util -s` and `ipmitool sel list | grep -i memory`.\n"
       "2. Map the reporting DIMM to a physical slot with `dmidecode -t memory`.\n"
       "3. If errors cluster on one module, replace that DIMM.\n"
       "4. If errors are spread across a channel, reseat every DIMM on that channel and clean the contacts before replacing anything.\n"
       "5. Clear counters and monitor for 24h under load before closing.",
       SRC_CONFIRMED),

    _e("Memory", "ECC_UCE",
       "Uncorrectable ECC error. The node panics or resets; the BMC records the failing DIMM location.",
       "SC-DR64G RDIMM; SC-MB2200 system board memory controller",
       "A hard fault in the memory device. A whole-channel or whole-controller pattern instead points at the processor's integrated memory controller or the board.",
       "1. Record the DIMM location from the SEL before rebooting.\n"
       "2. Replace the identified DIMM — an uncorrectable error is not a reseat candidate.\n"
       "3. Run a full memory test pass before returning the node to service.\n"
       "4. If uncorrectable errors follow the slot rather than the module, escalate to board replacement.\n"
       "5. Two or more DIMMs failing on the same channel in a short window means the controller, not the modules.",
       SRC_CONFIRMED),

    _e("Storage", "SMART_197",
       "SMART attribute 197 (Current Pending Sector Count) is non-zero and climbing on a SAS drive.",
       "SC-HD18T 18TB SAS 7.2K LFF drive",
       "Sectors that failed a read and are awaiting reallocation. A climbing pending count reliably precedes user-visible data errors.",
       "1. Capture full SMART data: `smartctl -a /dev/sdX`.\n"
       "2. Read attribute 197 together with 5 (Reallocated Sectors) and 198 (Offline Uncorrectable) — the three together tell you whether the drive is degrading or already failed.\n"
       "3. A non-zero, climbing 197 is a replacement, not a watch item.\n"
       "4. Confirm the array has rebuilt or the data is otherwise protected before pulling the drive.\n"
       "5. Hot-swap the drive and verify the rebuild starts.",
       SRC_CONFIRMED),

    _e("Storage", "NVME_MEDIA_ERR",
       "NVMe drive reports media and data integrity errors in its SMART log. The OS logs I/O errors against the device.",
       "SC-NV7T6 7.68TB U.2 NVMe drive; SC-BP24N backplane bay",
       "NAND media degradation, or a marginal U.2 connector. A drive that clears after reseating was a connector problem; one that does not is a media problem.",
       "1. Read the controller's own log: `nvme smart-log /dev/nvmeXn1`.\n"
       "2. Check the media error count together with percentage used and available spare.\n"
       "3. Reseat the drive once and re-read the log — a connector fault clears, a media fault does not.\n"
       "4. Replace if media errors persist or available spare is below threshold.\n"
       "5. Confirm the replacement enumerates at full PCIe link width before closing.",
       SRC_CONFIRMED),

    _e("Board", "BATT_P3V_RTC_LOW",
       "RTC battery voltage below threshold. System time drifts and BIOS settings are lost across AC removal.",
       "CR2032 RTC cell; SC-MB2200 system board",
       "A depleted RTC coin cell. Expected wear, not a fault, on nodes in service beyond a few years.",
       "1. Confirm with `ipmitool sensor list | grep -i batt` — the reading will be below 2.7V.\n"
       "2. Power down and remove AC. This is not a hot-swap operation.\n"
       "3. Replace the coin cell, observing polarity.\n"
       "4. Power on, enter BIOS setup, reapply the site's boot and power-restore settings, and set the clock.\n"
       "5. Confirm settings persist across a full AC removal before closing.",
       SRC_CONFIRMED),

    _e("BIOS", "CMOS_CHECKSUM",
       "CMOS checksum error on POST. BIOS settings revert to defaults and the node may boot to the wrong device.",
       "SC-MB2200 system board; RTC battery",
       "A depleted RTC battery, an interrupted BIOS update, or a corrupted NVRAM region.",
       "1. Check RTC battery voltage first — a flat cell is the common cause and the cheap fix.\n"
       "2. Replace the cell if low, then reapply BIOS settings.\n"
       "3. If the battery is healthy, load setup defaults, save, and power-cycle fully.\n"
       "4. If the checksum error returns with a good battery, reflash BIOS at the qualified level.\n"
       "5. Persistent corruption after a clean reflash means board replacement.",
       SRC_CONFIRMED),

    _e("BIOS", "POST_0xB2",
       "POST halts at code 0xB2 with no video output. Fans spin at full speed and the node never reaches boot device selection.",
       "SC-DR64G RDIMM; SC-CP9480 processor; SC-MB2200 system board",
       "Memory training failure. The memory reference code could not train one or more channels, most often because of a DIMM population error or a failed module.",
       "1. Read the POST code from the BMC rather than from the board LEDs — it is retained after the halt.\n"
       "2. Verify the DIMM population matches the documented order for the platform. Wrong population is the most common cause of this halt.\n"
       "3. Boot with a single DIMM in the first slot of the first channel to confirm the node trains at all.\n"
       "4. Add DIMMs back a channel at a time to isolate the failing module or slot.\n"
       "5. Clear CMOS before concluding the board is at fault — a stale training profile can reproduce this.",
       SRC_CONFIRMED),

    _e("Firmware", "BMC_UNRESPONSIVE",
       "BMC stops answering on the management network and the web interface times out. The host OS keeps running normally.",
       "CoreBMC management controller; SC-MB2200 system board",
       "A hung BMC firmware task. The host is unaffected because the BMC is out-of-band — this is a management-plane fault, not a host fault.",
       "1. Try an in-band cold reset first: `ipmitool mc reset cold` from the host OS.\n"
       "2. If in-band access is also dead, remove AC for 60s — BMC standby power must be fully drained for the controller to reinitialise.\n"
       "3. Confirm the BMC reaches its login page and the SEL is intact after recovery.\n"
       "4. Update BMC firmware to the qualified level if the hang has recurred.\n"
       "5. Repeated hangs at the current firmware level warrant board replacement.",
       SRC_CONFIRMED),

    _e("Firmware", "BMC_FW_MISMATCH",
       "BMC, BIOS and CPLD firmware are at levels that are not qualified together. Symptoms are inconsistent: spurious sensor readings, missing SEL entries, or sensors that never assert.",
       "CoreBMC firmware; BIOS; CPLD",
       "A partial firmware update — one component updated, the others left behind. Sensor thresholds and SEL decoding are defined across the firmware set, so a mismatch produces misleading telemetry.",
       "1. Record all three versions: `ipmitool mc info`, `dmidecode -t bios`, and the CPLD version from the log bundle.\n"
       "2. Check the set against the platform's qualified firmware matrix.\n"
       "3. Update in the documented order. Order matters — BMC before BIOS on SC platforms.\n"
       "4. Perform a full AC power cycle after the set is complete, not a warm reboot.\n"
       "5. Re-read sensors and confirm the telemetry is now consistent before trusting any earlier fault report from this node.",
       SRC_CONFIRMED),
]


# =========================================================================
# 2. GENERAL SERVER FAULT KB (29)
# =========================================================================
SERVER_FAULT_KB = [
    _e("Storage", "SAS_PHY_RESET",
       "SAS PHY reset storm logged against one drive bay. The drive drops and re-enumerates repeatedly.",
       "SC-HD18T SAS drive; SC-BP24N backplane; SC-RC940 RAID controller",
       "A marginal PHY link, usually from a contaminated or worn backplane connector, sometimes from a failing drive's own SAS interface.",
       "1. Identify the bay from the controller log: `storcli /c0 show events`.\n"
       "2. Move the suspect drive to a known-good bay. If the resets follow the drive, replace the drive; if they stay with the bay, the backplane is at fault.\n"
       "3. Inspect and clean the bay connector.\n"
       "4. Replace the backplane if resets persist with a known-good drive.",
       SRC_FAULT_KB),

    _e("Storage", "RAID_PD_FAILED",
       "RAID controller marks a physical drive failed and the virtual drive enters degraded state.",
       "SC-HD18T SAS drive; SC-RC940 RAID controller",
       "The drive exceeded the controller's error threshold. Occasionally a controller-side false positive after a transient bus event.",
       "1. Confirm the failure in the controller: `storcli /c0 /eall /sall show`.\n"
       "2. Read the drive's own SMART data before accepting the controller's verdict — a drive with clean SMART that was failed after a bus event may be recoverable.\n"
       "3. Replace the drive and confirm the rebuild starts and progresses.\n"
       "4. Do not pull a second drive from a degraded array under any circumstances.",
       SRC_FAULT_KB),

    _e("Storage", "BADSECTOR_PENDING",
       "Filesystem reports read errors on specific blocks while the drive still reports itself healthy overall.",
       "SC-HD18T SAS drive; SC-NV7T6 NVMe drive",
       "Localised media defects that have not yet crossed the drive's own failure threshold.",
       "1. Run a long self-test: `smartctl -t long /dev/sdX`, then read the result.\n"
       "2. Correlate the reported LBA with the filesystem errors.\n"
       "3. Any confirmed uncorrectable read is a replacement — the drive's overall health verdict is not the deciding factor.\n"
       "4. Verify data protection before pulling.",
       SRC_FAULT_KB),

    _e("Storage", "NVME_LINK_DEGRADED",
       "NVMe drive enumerates but negotiates a narrower or slower PCIe link than expected. Throughput is well below spec.",
       "SC-NV7T6 NVMe drive; SC-BP24N backplane; SC-RS16X riser",
       "A partially seated drive, a contaminated U.2 connector, or a degraded riser lane.",
       "1. Check the negotiated link: `lspci -vv -s <bdf> | grep -i lnksta`.\n"
       "2. Compare against the capability line — a x4 drive reporting x2 is the signature.\n"
       "3. Reseat the drive and re-read. Most cases clear here.\n"
       "4. If the bay consistently degrades any drive, replace the backplane; if a whole riser's bays degrade, replace the riser.",
       SRC_FAULT_KB),

    _e("Memory", "DIMM_TRAINING_FAIL",
       "One DIMM fails memory training and is mapped out. The node boots with reduced capacity.",
       "SC-DR64G RDIMM; SC-MB2200 system board DIMM slot",
       "A failed module, a bent slot contact, or debris in the slot.",
       "1. Identify the mapped-out slot from the BMC event and confirm with `dmidecode -t memory`.\n"
       "2. Move the DIMM to a known-good slot. If it trains there, the original slot is at fault.\n"
       "3. Inspect the suspect slot under good light for bent or displaced contacts.\n"
       "4. Replace the DIMM if it fails in a known-good slot; escalate to board replacement if the slot is damaged.",
       SRC_FAULT_KB),

    _e("Memory", "EDAC_CE_RATE",
       "EDAC reports a sustained correctable error rate across one memory channel rather than one module.",
       "SC-DR64G RDIMM (whole channel); SC-CP9480 integrated memory controller",
       "A channel-wide pattern points at the memory controller or the board trace, not at any single module.",
       "1. Read per-channel counters with `edac-util -s`.\n"
       "2. Confirm the pattern is channel-wide rather than concentrated on one DIMM — this is the distinction that decides the whole repair path.\n"
       "3. Reseat every module on the channel and retest before replacing anything.\n"
       "4. If the rate persists with all modules swapped out, the controller or board is at fault.",
       SRC_FAULT_KB),

    _e("Memory", "DIMM_THERMAL_THROTTLE",
       "Memory thermal throttling asserted. Memory bandwidth drops sharply under sustained load.",
       "SC-DR64G RDIMM; SC-FN80D fan module; air baffle",
       "Restricted airflow over the DIMM banks — most often a missing or misfitted air baffle, or a failed fan upstream.",
       "1. Read DIMM temperatures: `ipmitool sensor list | grep -i dimm`.\n"
       "2. Check the air baffle is present and correctly seated. A missing baffle is the most common cause and costs nothing to fix.\n"
       "3. Verify all fans are running and no module has lost a rotor.\n"
       "4. Check inlet temperature — if the whole node is running hot, this is a facilities problem.",
       SRC_FAULT_KB),

    _e("CPU", "CPU_MCE_BANK4",
       "Machine check exception logged against a processor cache bank. The node may survive or may panic depending on severity.",
       "SC-CP9480 processor",
       "An uncorrectable cache error within the processor. Not a serviceable sub-component.",
       "1. Decode the MCE: `mcelog --client` and cross-reference the kernel log.\n"
       "2. Note which socket and bank. Repeated MCEs on the same bank are conclusive.\n"
       "3. Update BIOS microcode to the qualified level — some MCE signatures are microcode-addressable.\n"
       "4. Replace the processor if MCEs recur after the microcode update.",
       SRC_FAULT_KB),

    _e("CPU", "UPI_LINK_DOWN",
       "An inter-socket link fails to train or drops at runtime. The node either boots single-socket or panics.",
       "SC-CP9480 processor; SC-MB2200 system board",
       "A seating or contact problem on one of the two sockets, or board trace damage between them.",
       "1. Record which link and which sockets from the SEL.\n"
       "2. Power down and reseat both processors — an inter-socket link fault can originate at either end.\n"
       "3. Inspect both sockets for bent pins.\n"
       "4. If the link still fails to train with both processors known good, replace the board.",
       SRC_FAULT_KB),

    _e("CPU", "CPU_THERMTRIP",
       "Thermal trip asserted. The processor shut the node down to protect itself.",
       "SC-CP9480 processor; heatsink; thermal interface material; SC-FN80D fans",
       "Heatsink contact failure — poorly applied thermal interface material, an under-torqued heatsink, or blocked airflow.",
       "1. Do not simply power the node back on and hope. Establish why it overheated.\n"
       "2. Check fan health and inlet temperature first.\n"
       "3. Remove the heatsink and inspect the thermal interface coverage — patchy or dried-out material is the usual finding.\n"
       "4. Clean both surfaces, reapply material, and retorque to the documented cross pattern.\n"
       "5. Run a sustained load test and watch temperatures before returning to service.",
       SRC_FAULT_KB),

    _e("Power", "PSU_OUTPUT_OC",
       "PSU asserts output overcurrent and shuts down. The node drops if the peer supply cannot carry the full load.",
       "SC-PS2000 power supply; SC-MB2200 system board; SC-XA400 accelerator modules",
       "A genuine downstream short, or a failing PSU misreporting. Accelerator nodes draw close to supply limits, so a real overcurrent is plausible there.",
       "1. Capture the SEL and the PSU's own fault history from the log bundle before removing AC.\n"
       "2. Attempt power-on with accelerators and risers removed. If it powers on cleanly, add them back one at a time.\n"
       "3. If minimum configuration also trips, swap the PSU with a known-good unit.\n"
       "4. A trip that follows a specific component is a component fault; one that stays with the slot is a PSU or board fault.",
       SRC_FAULT_KB),

    _e("Power", "PSU_FAN_FAIL",
       "PSU internal fan failure reported. The supply is still delivering power but will derate or shut down as it heats.",
       "SC-PS2000 power supply",
       "PSU internal fan wear. The fan is not separately serviceable.",
       "1. Confirm which slot is asserting.\n"
       "2. Verify the peer PSU is healthy before removing anything.\n"
       "3. Hot-swap the affected supply — this is not a watch item, the unit will derate.\n"
       "4. Confirm the replacement shares load correctly.",
       SRC_FAULT_KB),

    _e("Power", "PWR_GOOD_TIMEOUT",
       "Power-good signal not asserted within the expected window. The node attempts power-on and immediately returns to standby.",
       "SC-MB2200 system board; SC-PS2000 power supply; SC-CP9480 processor",
       "A rail failing to come up in sequence. Can originate at the supply, the board VRs, or a processor preventing the sequence from completing.",
       "1. Read the failing sequence step from the BMC log — it names the rail that did not come up.\n"
       "2. Remove AC for 60s and retry; a stuck sequencer often clears.\n"
       "3. Retry at minimum configuration.\n"
       "4. Substitute a known-good PSU before condemning the board.",
       SRC_FAULT_KB),

    _e("Thermal", "INLET_TEMP_HIGH",
       "Inlet temperature above threshold. Fans run at maximum and the node may throttle.",
       "Chassis inlet sensor; rack airflow; facility cooling",
       "An environmental condition, not a node fault — a blocked inlet, missing blanking panels, hot-aisle recirculation, or a cooling failure in the hall.",
       "1. Read the inlet sensor and compare against neighbouring nodes in the same rack.\n"
       "2. If neighbours read the same, this is a facilities issue — escalate rather than touching the node.\n"
       "3. If only this node is hot, check for a blocked inlet, missing blanking panels, or a cable obstruction.\n"
       "4. Replace the inlet sensor only when the reading is inconsistent with a physical measurement at the inlet.",
       SRC_FAULT_KB),

    _e("Thermal", "EXHAUST_TEMP_HIGH",
       "Exhaust temperature high with inlet temperature normal. The node is not shedding heat.",
       "SC-FN80D fan modules; air baffle; heatsinks; SC-XA400 accelerator modules",
       "Reduced airflow through the chassis or an unusually high internal heat load.",
       "1. Confirm inlet is normal — that is what distinguishes this from a facilities problem.\n"
       "2. Check every fan is present and both rotors running.\n"
       "3. Verify the air baffle and all blanking panels are fitted. An open bay short-circuits chassis airflow.\n"
       "4. On accelerator nodes, check per-module temperatures for one module running far hotter than its peers.",
       SRC_FAULT_KB),

    _e("Network", "NIC_LINK_FLAP",
       "Network interface repeatedly loses and regains link. Traffic is disrupted in bursts.",
       "SC-NX200 OCP adapter; optical transceiver; fibre patch lead; switch port",
       "A marginal optical link — a dirty or damaged connector, a failing transceiver, or a switch-side port fault. The adapter itself is the least likely cause.",
       "1. Read the interface counters and link history: `ethtool ethX` and `dmesg | grep -i link`.\n"
       "2. Read transceiver diagnostics: `ethtool -m ethX`. Low receive power points at the fibre path.\n"
       "3. Clean both fibre end faces before replacing anything — contamination is the single most common cause.\n"
       "4. Swap the transceiver, then the patch lead, then move to a different switch port, in that order.\n"
       "5. Replace the adapter only after the fibre path and switch port are eliminated.",
       SRC_FAULT_KB),

    _e("Network", "OCP_PRESENCE_LOST",
       "OCP adapter no longer detected. The interface disappears from the OS and the BMC inventory.",
       "SC-NX200 OCP adapter; OCP slot on SC-MB2200",
       "A partially seated adapter or a failed slot.",
       "1. Confirm absence from PCIe enumeration: `lspci | grep -i ether`.\n"
       "2. Power down — OCP 3.0 slots on SC platforms are not hot-swap.\n"
       "3. Reseat the adapter fully until the latch engages.\n"
       "4. If a known-good adapter is also not detected, the slot or board is at fault.",
       SRC_FAULT_KB),

    _e("Network", "PCIE_CE_RATE",
       "PCIe correctable error rate above threshold on one device. Throughput may be reduced; the device stays functional.",
       "SC-RS16X riser; SC-NX200 adapter; SC-MB2200 system board",
       "Signal integrity degradation on the link — a marginal riser connection or a contaminated slot.",
       "1. Read AER counters from the kernel log and confirm they are correctable, not fatal.\n"
       "2. Note the negotiated link width and speed.\n"
       "3. Reseat the device and its riser.\n"
       "4. Move the device to another slot. If errors follow the device, replace it; if they stay with the slot, replace the riser.",
       SRC_FAULT_KB),

    _e("Network", "PCIE_UE_FATAL",
       "Fatal PCIe uncorrectable error. The device drops off the bus and the node may panic.",
       "SC-RS16X riser; SC-NX200 adapter; SC-XA400 accelerator module",
       "A hard link failure — a failed device, a failed riser, or a power delivery problem on the slot.",
       "1. Capture the full AER decode and the SEL before rebooting.\n"
       "2. Check whether a rail event was logged at the same time. If so, treat as a power fault first.\n"
       "3. Reseat the device and riser.\n"
       "4. Swap the device to another slot to determine whether the fault follows the device or the slot.",
       SRC_FAULT_KB),

    _e("BIOS", "BOOT_NO_MEDIA",
       "No bootable media found. The node reaches boot device selection and stops.",
       "Boot drive; SC-RC940 RAID controller; BIOS boot order",
       "A lost boot order after a CMOS clear, a failed boot drive, or a degraded boot array.",
       "1. Check whether the boot device enumerates at all in BIOS setup.\n"
       "2. If it enumerates, this is a boot order problem — reapply the site's boot configuration.\n"
       "3. If it does not, check the controller for a failed or foreign-state drive.\n"
       "4. Check RTC battery health — a flat cell loses boot order repeatedly and is the real fix.",
       SRC_FAULT_KB),

    _e("BIOS", "POST_0xA9",
       "POST halts at code 0xA9 during PCIe enumeration. No video, no boot.",
       "SC-RS16X riser; SC-XA400 accelerator module; SC-NX200 adapter",
       "A PCIe device preventing enumeration from completing — a failed device or a riser fault.",
       "1. Read the POST code from the BMC.\n"
       "2. Remove all PCIe devices and risers, then power on. Reaching POST confirms a device is at fault.\n"
       "3. Add devices back one at a time until the halt reproduces.\n"
       "4. Replace the identified device or riser.",
       SRC_FAULT_KB),

    _e("BIOS", "BIOS_UPDATE_FAIL",
       "BIOS update aborts partway. The node may fail to POST afterwards.",
       "BIOS flash; CoreBMC firmware",
       "An interrupted update — usually a power event during the flash window, or an image that does not match the platform.",
       "1. Do not power-cycle repeatedly. That risks corrupting a recovery image as well.\n"
       "2. Verify the image matches the exact platform SKU, not just the family.\n"
       "3. Use the BMC's out-of-band recovery flash rather than an in-band retry.\n"
       "4. If recovery flash also fails, the board needs replacement.",
       SRC_FAULT_KB),

    _e("Firmware", "CPLD_VER_MISMATCH",
       "CPLD version does not match the qualified set. Power sequencing or presence detection behaves inconsistently.",
       "CPLD on SC-MB2200; CoreBMC firmware",
       "A partial firmware update. The CPLD drives power sequencing and presence detect, so a mismatch produces symptoms that look like hardware faults.",
       "1. Read the CPLD version from the log bundle.\n"
       "2. Compare against the platform's qualified firmware matrix.\n"
       "3. Update the CPLD, then perform a full AC power cycle — a CPLD update does not take effect on a warm reboot.\n"
       "4. Re-verify any earlier presence or sequencing fault from this node; it may have been the mismatch all along.",
       SRC_FAULT_KB),

    _e("Firmware", "SEL_FULL",
       "System event log full. New events are dropped, so the node stops reporting faults.",
       "CoreBMC event log",
       "The SEL was never cleared after previous events. Not a fault in itself, but it blinds you to real faults.",
       "1. Export the full SEL before clearing — you are about to destroy the node's fault history.\n"
       "2. `ipmitool sel save` then `ipmitool sel clear`.\n"
       "3. Review the exported log for unaddressed faults.\n"
       "4. Add SEL capacity to routine monitoring so this does not recur.",
       SRC_FAULT_KB),

    _e("Firmware", "BMC_SENSOR_STALE",
       "One or more BMC sensors report a fixed value or no reading at all, while the hardware is demonstrably fine.",
       "CoreBMC firmware; sensor cabling",
       "A stalled sensor polling task, a firmware mismatch, or a disconnected sensor lead.",
       "1. Cold-reset the BMC: `ipmitool mc reset cold`. Most stale sensors clear here.\n"
       "2. Re-read the sensor and confirm it tracks a real change.\n"
       "3. Check the firmware set is qualified together — mismatches commonly present this way.\n"
       "4. Do not act on a stale sensor's reading. Confirm any fault it reports by another means first.",
       SRC_FAULT_KB),

    _e("Board", "RISER_LINK_DEGRADED",
       "Every device behind one riser negotiates a degraded link, or the riser's devices disappear entirely.",
       "SC-RS16X riser; riser slot on SC-MB2200",
       "A partially seated or failed riser. A whole riser's worth of devices behaving badly at once is the distinguishing signature.",
       "1. Check link status for every device behind the riser. A common pattern across all of them points at the riser.\n"
       "2. Power down and reseat the riser fully.\n"
       "3. Inspect the riser's board-edge connector for contamination or damage.\n"
       "4. Replace the riser; replace the board only if a known-good riser also degrades.",
       SRC_FAULT_KB),

    _e("Board", "CHASSIS_INTRUSION",
       "Chassis intrusion asserted. Logged as a security event.",
       "Chassis intrusion switch; top cover",
       "A cover that was opened for service, or an intrusion switch not making contact because the cover is not fully seated.",
       "1. Confirm the cover is fully closed and latched.\n"
       "2. Clear the event and check whether it re-asserts.\n"
       "3. If it re-asserts with the cover closed, the switch or its lead is at fault.\n"
       "4. Correlate against the maintenance record before treating it as a genuine security event.",
       SRC_FAULT_KB),

    _e("Board", "FRU_READ_FAIL",
       "FRU inventory read fails. Model and serial fields come back empty or corrupted in the BMC inventory.",
       "FRU EEPROM on SC-MB2200; CoreBMC firmware",
       "A corrupted FRU EEPROM, or a BMC unable to complete the read.",
       "1. Attempt the read directly: `ipmitool fru print`.\n"
       "2. Cold-reset the BMC and retry — a transient read failure clears here.\n"
       "3. If the read consistently fails, the EEPROM is corrupt.\n"
       "4. A node with an unreadable FRU cannot be reliably inventoried; flag it for board replacement rather than leaving it in service unidentified.",
       SRC_FAULT_KB),

    _e("System", "UNEXPECTED_REBOOT",
       "Node rebooted with no OS-side shutdown record and no obvious hardware event.",
       "SC-MB2200 system board; SC-PS2000 power supply; CoreBMC firmware",
       "Could be a power event, a watchdog expiry, an uncaught MCE, or an upstream facility event. The SEL timestamp is what separates them.",
       "1. Read the SEL and find the last event before the reboot. That timestamp is the whole investigation.\n"
       "2. Check for AC loss events on either PSU — an upstream power event looks exactly like a crash from inside the OS.\n"
       "3. Check for watchdog expiry, which points at a hung host rather than a hardware fault.\n"
       "4. Check for an MCE or IERR immediately before the reset.\n"
       "5. With a genuinely empty SEL, look upstream at the rack before suspecting the node.",
       SRC_FAULT_KB),
]


# =========================================================================
# 3. PLATFORM-SPECIFIC FAULTS (14) — SC family quirks
# =========================================================================
PLATFORM_FAULTS = [
    _e("Storage", "SMART_5",
       "SMART attribute 5 (Reallocated Sector Count) climbing on an SC-1150S storage node LFF drive.",
       "SC-HD18T 18TB SAS drive",
       "Sectors already reallocated from the spare pool. A climbing count means the pool is being consumed.",
       "1. Read attributes 5, 197 and 198 together — the trio, not attribute 5 alone, tells you the trajectory.\n"
       "2. A stable non-zero count on an older drive is normal wear; a climbing count is a replacement.\n"
       "3. Confirm array protection, then hot-swap.\n"
       "4. On SC-1150S, verify the replacement is recognised by the controller before closing — LFF bays on this platform need the carrier fully latched to make the SAS connection.",
       SRC_PLATFORM),

    _e("Storage", "SMART_187",
       "SMART attribute 187 (Reported Uncorrectable Errors) non-zero. The drive has returned data it could not correct.",
       "SC-HD18T SAS drive; SC-NV7T6 NVMe drive",
       "Uncorrectable read errors reached the host. Data loss has already occurred on those blocks.",
       "1. Any non-zero value here is significant — unlike pending sectors, these errors reached the application.\n"
       "2. Verify the array rebuilt or the data was protected.\n"
       "3. Replace the drive.\n"
       "4. Check whether the filesystem logged corresponding errors, and flag affected data.",
       SRC_PLATFORM),

    _e("Storage", "SMART_198",
       "SMART attribute 198 (Offline Uncorrectable) non-zero after a background scan.",
       "SC-HD18T SAS drive",
       "The drive's own background scan found sectors it cannot read. These have not yet been hit by the host.",
       "1. Run a long self-test to confirm.\n"
       "2. Treat as a pre-failure indicator — schedule replacement rather than waiting for host-visible errors.\n"
       "3. Replace at the next maintenance window unless the count is climbing quickly.",
       SRC_PLATFORM),

    _e("Memory", "SC_DIMM_POP_ORDER",
       "SC-3300M quad-socket node boots with far less memory than installed, or halts at memory training.",
       "SC-DR64G RDIMM; SC-MB2200 memory slots",
       "DIMM population does not follow the platform's documented order. On SC-3300M the population rule differs from the two-socket platforms and is the most common cause of a capacity mismatch on this model.",
       "1. Compare installed population against the documented order for SC-3300M specifically — do not assume the SC-2200R rule applies.\n"
       "2. Repopulate to the documented order.\n"
       "3. Clear CMOS to discard the stale training profile, then power on.\n"
       "4. Confirm full capacity in BIOS and in the OS before closing.",
       SRC_PLATFORM),

    _e("Memory", "SC_DIMM_MIXED_RANK",
       "Memory runs below rated speed, or training fails intermittently, on a node with mixed DIMM types.",
       "SC-DR64G RDIMM and other DDR5 modules",
       "Mixed rank or mixed speed modules within a channel. The controller falls back to the lowest common denominator or fails to train at all.",
       "1. Inventory every module: `dmidecode -t memory` and compare part numbers, ranks and speeds.\n"
       "2. Any mismatch within a channel explains the symptom.\n"
       "3. Standardise the channel on a single module type.\n"
       "4. Do not mix a replacement DIMM of a different rank into an existing channel — pull matching modules instead.",
       SRC_PLATFORM),

    _e("GPU", "SC_XA400_POWER_CABLE",
       "SC-XA400 accelerator not detected, or detected then dropping under load, on an SC-4800G node.",
       "SC-XA400 accelerator module; auxiliary power cabling; SC-RS16X riser",
       "An auxiliary power connector not fully latched. Under idle the module may enumerate; under load it browns out and drops.",
       "1. A module that enumerates at idle but drops under load is almost always a power cabling problem, not a module fault.\n"
       "2. Power down and reseat both ends of every auxiliary power lead to the affected module.\n"
       "3. Confirm each connector latches audibly.\n"
       "4. Run a sustained load test before returning to service — an idle check will not reproduce this.",
       SRC_PLATFORM),

    _e("GPU", "SC_XA400_THERMAL_SKEW",
       "One SC-XA400 module runs 15-20C hotter than its peers in the same SC-4800G chassis.",
       "SC-XA400 accelerator module; air baffle; SC-FN80D fans",
       "Airflow maldistribution — a misfitted baffle, a missing blanking panel, or a heatsink contact problem on that module.",
       "1. Read all eight module temperatures and confirm the skew is real and sustained, not a transient load imbalance.\n"
       "2. Check the baffle and blanking panels around the hot module.\n"
       "3. Confirm fan health upstream of that position.\n"
       "4. If airflow is confirmed good, the module's own heatsink contact is suspect — escalate for module replacement.",
       SRC_PLATFORM),

    _e("Power", "SC_PSU_MIXED_RATING",
       "PSUs fail to share load, or the node refuses to power on with both supplies installed.",
       "SC-PS2000 power supply",
       "Mismatched supply ratings or firmware levels in the same chassis. SC platforms require matched pairs.",
       "1. Read both supplies' model and firmware: `ipmitool fru print` and the PSU entries in the log bundle.\n"
       "2. Any rating or firmware mismatch explains the symptom.\n"
       "3. Replace so both supplies match.\n"
       "4. On SC-4800G this matters more than on the other platforms — accelerator nodes cannot run on one supply under load.",
       SRC_PLATFORM),

    _e("Thermal", "SC_BAFFLE_MISSING",
       "Multiple thermal warnings across unrelated components — DIMMs, processors and accelerators all running warm simultaneously.",
       "Air baffle; SC-FN80D fans",
       "The air baffle is missing or misfitted, so chassis airflow bypasses the components it is meant to direct air across.",
       "1. Simultaneous warnings across unrelated components is the signature — a component fault does not produce this pattern.\n"
       "2. Open the node and check the baffle is present, correctly oriented, and fully seated.\n"
       "3. Check every blanking panel and drive blank is fitted.\n"
       "4. Close up and confirm temperatures normalise under load.",
       SRC_PLATFORM),

    _e("BIOS", "SC_BOOT_MODE_MISMATCH",
       "Node will not boot an installed OS after a board or BIOS change. The drive enumerates correctly.",
       "BIOS boot mode setting; boot drive",
       "Boot mode reverted to the platform default and no longer matches how the OS was installed.",
       "1. Check the current boot mode against how the OS was installed.\n"
       "2. A replaced board or a CMOS clear resets this to the platform default — a very common post-repair symptom.\n"
       "3. Set the mode to match the installation, save, and reboot.\n"
       "4. Record the site's required setting so the next board swap does not repeat this.",
       SRC_PLATFORM),

    _e("Firmware", "SC_FW_UPDATE_ORDER",
       "Firmware update leaves the node in an inconsistent state — sensors missing, or the BMC reporting the old BIOS version.",
       "CoreBMC firmware; BIOS; CPLD",
       "Components updated out of order. SC platforms require BMC first, then BIOS, then CPLD, with a full AC cycle at the end.",
       "1. Read all three current versions.\n"
       "2. Redo the update in the documented order — BMC, BIOS, CPLD. Order is not advisory on this platform.\n"
       "3. Perform a full AC power cycle, not a warm reboot.\n"
       "4. Confirm all three versions read back correctly before closing.",
       SRC_PLATFORM),

    _e("Network", "SC_OCP_SLOT_LANE",
       "SC-NX200 adapter negotiates x8 instead of x16 in the OCP slot on SC-2400H.",
       "SC-NX200 OCP adapter; OCP slot; SC-RS16X riser",
       "On SC-2400H the OCP slot shares lanes with riser 2. Populating riser 2 bifurcates the OCP slot to x8 by design.",
       "1. Confirm the negotiated width with `lspci -vv | grep -i lnksta`.\n"
       "2. Check whether riser 2 is populated. If it is, this is expected platform behaviour, not a fault.\n"
       "3. If full width is required, move the riser 2 device or accept the narrower link.\n"
       "4. Do not replace the adapter for this symptom on SC-2400H.",
       SRC_PLATFORM),

    _e("Board", "SC_BP_CABLE_ORDER",
       "Drive bay numbering in the OS does not match the physical bay labels after a backplane or cable replacement.",
       "SC-BP24N backplane; backplane sideband cabling",
       "Backplane cables connected in the wrong order. Bays enumerate, but the mapping is scrambled — which means a subsequent drive replacement pulls the wrong drive.",
       "1. Treat this as urgent. A scrambled map will cause someone to pull a healthy drive from a degraded array.\n"
       "2. Verify the cable order against the documented mapping for the platform.\n"
       "3. Correct the cabling and confirm bay 1 in the OS is physically bay 1.\n"
       "4. Verify the full mapping bay by bay before returning the node to service.",
       SRC_PLATFORM),

    _e("Board", "SC_RISER_SLOT_PRIORITY",
       "A PCIe device works in one riser slot but not another on the same SC-2200R node.",
       "SC-RS16X riser; SC-MB2200 system board",
       "Slot lane allocation differs between riser positions on SC-2200R. Not every slot provides full width or the same bifurcation options.",
       "1. Check the slot's documented lane allocation before assuming a fault.\n"
       "2. Confirm the device's width requirement against what the slot provides.\n"
       "3. Move the device to a slot that meets its requirement.\n"
       "4. This is a configuration constraint, not a hardware fault — do not raise a parts request.",
       SRC_PLATFORM),
]


# =========================================================================
# 4. ACCELERATOR FAULTS (10)
# =========================================================================
ACCEL_FAULTS = [
    _e("GPU", "XID_212_FALLEN_OFF_BUS",
       "Accelerator module drops off the PCIe bus at runtime. Workloads fail and the module disappears from inventory until reboot.",
       "SC-XA400 accelerator module; SC-RS16X riser; auxiliary power cabling",
       "A hard fault on the module, a power delivery failure, or a riser link failure. All three present identically.",
       "1. Capture the kernel log around the event and the BMC SEL for the same timestamp.\n"
       "2. Check for a rail or PSU event in the same second. If present, treat as a power fault first.\n"
       "3. Power down and reseat the module, its riser and its auxiliary power leads.\n"
       "4. Move the module to a different slot. If the fault follows the module, replace it; if it stays with the slot, replace the riser.",
       SRC_ACCEL),

    _e("GPU", "XID_233_UNCONTAINED_ECC",
       "Uncontained ECC error on accelerator on-die memory. The affected workload is killed and the module requires a reset.",
       "SC-XA400 accelerator module",
       "An uncorrectable memory error on the module that could not be contained to a single process.",
       "1. Record the module's bus ID and the exact error from the kernel log.\n"
       "2. Read the module's own error counters and retired-page status.\n"
       "3. A single uncontained event may be recoverable with a module reset; a repeat on the same module is a replacement.\n"
       "4. Run a memory diagnostic pass on the module before returning it to service.",
       SRC_ACCEL),

    _e("GPU", "XID_198_REMAP_PENDING",
       "Accelerator reports memory rows pending remap. The module still functions but has retired capacity.",
       "SC-XA400 accelerator module",
       "Memory rows retired after correctable errors. Expected in small numbers; significant when climbing.",
       "1. Read the remapped-row counters and compare against the module's threshold.\n"
       "2. A pending remap requires a module reset to take effect — the module is not fully healthy until it does.\n"
       "3. Drain the node, reset the module, and confirm the remap completed.\n"
       "4. Replace if rows continue to be retired after the remap.",
       SRC_ACCEL),

    _e("GPU", "XID_205_DOUBLE_BIT",
       "Double-bit error on accelerator memory. The module is unusable until reset.",
       "SC-XA400 accelerator module",
       "An uncorrectable double-bit error in on-die memory.",
       "1. Capture the full error report and the module bus ID.\n"
       "2. Reset the module and re-run diagnostics.\n"
       "3. A double-bit error that recurs on the same module is conclusive — replace.\n"
       "4. Check whether the module is also running thermally hot; sustained over-temperature raises error rates.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_THERMAL_SLOWDOWN",
       "Accelerator clocks drop sharply under load. Throughput falls well below expected without any error being logged.",
       "SC-XA400 accelerator module; SC-FN80D fans; air baffle",
       "Thermal throttling. The module is protecting itself and reporting no fault because nothing has failed.",
       "1. Read module temperatures and clock states under load, not at idle.\n"
       "2. Compare against peer modules in the same chassis.\n"
       "3. Check airflow — baffle, blanking panels and fan health.\n"
       "4. If one module alone is hot with airflow confirmed good, its heatsink contact is suspect.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_LINK_WIDTH_LOW",
       "Accelerator negotiates a narrower PCIe link than the slot provides. Host-to-module transfers are slow.",
       "SC-XA400 accelerator module; SC-RS16X riser",
       "A partially seated module or riser, or a contaminated slot.",
       "1. Read the negotiated width and compare against the capability line.\n"
       "2. Reseat the module and riser.\n"
       "3. Re-read after reseating — most cases clear here.\n"
       "4. Move to another slot to determine whether the fault follows the module or the slot.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_ECC_DISABLED",
       "Accelerator reports ECC disabled. Memory errors will go undetected.",
       "SC-XA400 accelerator module",
       "ECC was disabled in the module's persistent configuration, usually deliberately during a previous investigation and never re-enabled.",
       "1. Read the current ECC state for every module in the node.\n"
       "2. Re-enable ECC and reset the module for the change to take effect.\n"
       "3. Confirm the state persists across a reboot.\n"
       "4. Treat any error history collected while ECC was disabled as unreliable.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_INFOROM_CORRUPT",
       "Accelerator's on-module information store reports corruption. Inventory and error history are unreliable.",
       "SC-XA400 accelerator module",
       "Corruption in the module's persistent configuration and history store.",
       "1. Confirm the corruption is reported consistently across reboots.\n"
       "2. Note that the module's own error history can no longer be trusted for diagnosis.\n"
       "3. A module that cannot record its own error history should not stay in production.\n"
       "4. Replace the module.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_PEER_LINK_DOWN",
       "Inter-module link between two accelerators is down. Multi-module workloads fail or fall back to host-mediated transfers.",
       "SC-XA400 accelerator modules; inter-module bridge connector",
       "A bridge connector not fully seated, or a failed link on one of the two modules.",
       "1. Identify both endpoints from the link topology.\n"
       "2. Power down and reseat the bridge connector at both ends.\n"
       "3. If the link stays down, swap the bridge before suspecting either module.\n"
       "4. If a known-good bridge also fails, isolate which of the two modules is at fault by testing each against a third.",
       SRC_ACCEL),

    _e("GPU", "ACCEL_NOT_ENUMERATED",
       "One or more accelerator modules absent from PCIe enumeration after a reboot. The node otherwise boots normally.",
       "SC-XA400 accelerator module; SC-RS16X riser; auxiliary power cabling",
       "A seating, riser or power delivery problem. A module that was working before a reboot and is now absent is rarely a module failure.",
       "1. Count modules in `lspci` and compare against the expected population.\n"
       "2. Check the POST code — a halt during PCIe enumeration points at a device fault.\n"
       "3. Power down and reseat the missing module, its riser and its power leads.\n"
       "4. Check for a rail event in the SEL from the last power-on.",
       SRC_ACCEL),
]
