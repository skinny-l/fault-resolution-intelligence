"""Real sample tickets used to verify the parser (no server needed)."""

HDD_TICKET = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
硬盘VR状态/Disk Virtual Return Status：forced_non_return强制不返还
Priority：normal
可以直接维修
server_model：SC-2400H server_product：SCH2400-D2-N48
服务器SN/Server SN：DSN000003
机柜位置/Location：TESTDC1_B4_DH1B-B-10
起始U位/ unit_no: 40
server_po：
server_ip：fdbd:beef:cafe:100::1
服务器资产编号/asset_no:2024-is-srv-0000001
部件位置/part_position:22
背板号/backplane_number:0
服务器厂商/manufacturer:SynthCore
部件厂商/part_manufacturer:SynthCore
固件版本/firmware_version:SC03
部件SN/part_sn:PSN-DEMO-0001
部件容量/part_size:20TB
部件类型/part_type:HDD
部件PN/part_pn:SC-HD20T
fault_log_dir:None
故障明细/Fault_Detail:HDD: 0 < (BadSectorCount) < Min & (IOErrorWeek) > Min
故障设备/fault_part：sdw
故障类型/fault_type:Disk
故障描述/Fault Description:IOErrorWeekCount: (678) > 50 and HDDReallocatedSectors: 0 < (32) <= 200
30天内重复报修次数/fault_30day_rt：0
manufacturer_id：530666

From <https://portal.example.invalid/tickets/view.htm?id=100001&taskId=00000000-0000-4000-8000-000000000001>
"""

HDD_TICKET_NUMBER = "TKTA0000000003"

# Dispatch/assignment table sample — one row, matching HDD_TICKET's server SN.
# Note the dispatch ticket number ("...9999") deliberately differs from
# HDD_TICKET_NUMBER above, to prove the merge overrides the manually-typed
# ticket number rather than just filling in when blank.
DISPATCH_ROW_HDD = """Date
Ticket No#
Case ID#
Server SN
Rack Info
Faulty Part
OLD PN
NEW PN
Maker
Model
Engineer
2/7/2026
TKTA0000000004
TKTB0000000003
DSN000003
TESTDC1_B4_DH1B-B-10-40
Hard drive
PN-DEMO-0010
PN-DEMO-0012
Q
MPN-DEMO-0001
Taylor Deliver onsite"""

# Real dispatch table sample: one ticket number covering two parts on the
# same server (Motherboard + Memory), used to test category disambiguation.
DISPATCH_TABLE_TWO_PARTS = """Date
Ticket No#
Case ID#
Server SN
Rack Info
Faulty Part
OLD PN
NEW PN
Maker
Model
Engineer
2/7/2026
TKTA0000000005
TKTB0000000004
DSN000007
TESTDC2_B1_G1-V-14-13
Motherboard - high risk have bent pins
YZMB-02666-106
YZMB-02666-106 borrow
Q
MPN-DEMO-0002
Taylor Deliver onsite
2/7/2026
TKTA0000000005
TKTB0000000004
DSN000007
TESTDC2_B1_G1-V-14-13
Memory
PN-DEMO-0007
PN-DEMO-0007
Q
MPN-DEMO-0002
Taylor Deliver onsite"""

# Real-world case: ONE fault-description block (one job) but the dispatch
# table carries two rows for the same ticket/server SN — Memory and
# Motherboard both replaced under one ticket. Used to verify that both
# parts land in a single report instead of one PN being dropped, and
# instead of the ticket being split into two separate block reports.
MB_TICKET = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-2400H server_product：SCH2400-D2-N48
服务器SN/Server SN：DSN000004
机柜位置/Location：TESTDC1_B2_DH1A-H-10
起始U位/ unit_no: 33
服务器厂商/manufacturer:SynthCore
部件厂商/part_manufacturer:SynthCore
部件类型/part_type:Motherboard
故障明细/Fault_Detail:Memory CE (Count) > Max (Kernel)
故障类型/fault_type:Memory
故障描述/Fault Description:Memory CE (Count) > Max (Kernel)
30天内重复报修次数/fault_30day_rt：0
"""

MB_TICKET_NUMBER = "TKTA0000000006"

DISPATCH_TABLE_MB_PLUS_MEMORY = """Date
Ticket No#
Case ID#
Server SN
Rack Info
Faulty Part
OLD PN
NEW PN
Maker
Model
Engineer
10/7/2026
TKTA0000000006
TKTB0000000005
DSN000004
TESTDC1_B2_DH1A-H-10-33
Memory
PN-DEMO-0005
PN-DEMO-0005
I
SCH2400-D2-N48
Jordan | Casey | Sam Deliver onsite
10/7/2026
TKTA0000000006
TKTB0000000005
DSN000004
TESTDC1_B2_DH1A-H-10-33
Motherboard
YZMB-03296-10F
YZMB-03296-10F
I
SCH2400-D2-N48
Jordan | Casey | Sam Deliver onsite"""

# Real-world case: TWO 工单标签/tags fault blocks under one ticket — same
# server SN, two distinct GPU Xid events (Xid 95 uncontained ECC, and a
# separate remapped-rows event) — but only ONE dispatch-table row for that
# server SN (the GPU itself was only dispatched once). Used to verify the
# two blocks combine into a single note (shared header, one Remark) with
# each block keeping its own Details line and its own part data, instead
# of rendering as two fully separate reports.
GPU_TWO_BLOCK_TICKET = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-4800G server_product：SCG4800-D2-X8
服务器SN/Server SN：2KX100003
机柜位置/Location：TESTDC1_B2_DH2A-A-04
起始U位/ unit_no: 11
服务器厂商/manufacturer:SynthCore
部件位置/part_position:37:00
故障明细/Fault_Detail:xid 95 Uncontained ECC error occurred
故障类型/fault_type:GPU
故障描述/Fault Description:diff:371;NVRM: Xid (PCI:0000:37:00): 95, pid=5171, Uncontained: FBHUB. RST: Yes, D-RST: No
30天内重复报修次数/fault_30day_rt：0
工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-4800G server_product：SCG4800-D2-X8
服务器SN/Server SN：2KX100003
机柜位置/Location：TESTDC1_B2_DH2A-A-04
起始U位/ unit_no: 11
服务器厂商/manufacturer:SynthCore
部件位置/part_position:0000:37:00.0
部件厂商/part_manufacturer:SynthCore
部件SN/part_sn:1000000000001
部件PN/part_pn:900-21001-0020-100
故障明细/Fault_Detail:Remapped Rows pending With Volatile DRAM Uncorrectable > 0
故障类型/fault_type:GPU
故障描述/Fault Description:RemappedRows Pending:Yes,Volatile DRAMUncorrectable:2, need to reset GPU or server.
30天内重复报修次数/fault_30day_rt：0
"""

GPU_TICKET_NUMBER = "TKTA0000000007"

DISPATCH_ROW_GPU_SINGLE = """Date
Ticket No#
Case ID#
Server SN
Rack Info
Faulty Part
OLD PN
NEW PN
Maker
Model
Engineer
12/7/2026
TKTA0000000007
TKTB0000000006
2KX100003
TESTDC1_B2_DH2A-A-04-11
GPU A100 PCIE - SPEX2026071100090
0000:37:00.0 SN: 1000000000001
run FD and collect logs update in sheet first
A
SC-4800G
Morgan"""

# Real-world bug case: TWO separate 工单标签/tags fault blocks, both
# physically RAM (two DIMMs, two slots), same ticket/server SN — but the
# dispatch table collapses both into a single "Memory x2" row (one PN for
# both units) alongside separate Motherboard and NIC rows for parts that
# have no fault-description block of their own. Regression for a bug where
# the second RAM block, finding no same-category row left (the "x2" row
# had been treated as exhausted after the first match), fell back to the
# Motherboard row — mixing RAM's own Model/SN/MPN with Motherboard's PN
# under an incorrectly-titled "Old Motherboard" block.
RAM_X2_BLOCK_1 = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-2400H server_product：MPN-DEMO-0002
服务器SN/Server SN：DSN000005
机柜位置/Location：TESTDC1_F2_DHGA-A-21
起始U位/ unit_no: 17
服务器厂商/manufacturer:SynthCore
部件位置/part_position:P1_C3_D0
部件厂商/part_manufacturer:SynthCore
部件SN/part_sn:802C0F0000001AC
部件容量/part_size:64GB
部件类型/part_type:RAM
部件PN/part_pn:MTC40F2046S1RC56BD1
fault_log_dir:None
故障明细/Fault_Detail:Memory CE
故障类型/fault_type:Memory
故障描述/Fault Description:Memory CE (Count) > Max (Kernel)
30天内重复报修次数/fault_30day_rt：0
"""

RAM_X2_BLOCK_2 = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-2400H server_product：MPN-DEMO-0002
服务器SN/Server SN：DSN000005
机柜位置/Location：TESTDC1_F2_DHGA-A-21
起始U位/ unit_no: 17
服务器厂商/manufacturer:SynthCore
部件位置/part_position:P1_C5_D0
部件厂商/part_manufacturer:SynthCore
部件SN/part_sn:802C0F0000002AE
部件容量/part_size:64GB
部件类型/part_type:RAM
部件PN/part_pn:MTC40F2046S1RC56BD1
fault_log_dir:None
故障明细/Fault_Detail:Memory CE
故障类型/fault_type:Memory
故障描述/Fault Description:Memory CE (Count) > Max (Kernel)
30天内重复报修次数/fault_30day_rt：0
"""

RAM_X2_TICKET = RAM_X2_BLOCK_1 + RAM_X2_BLOCK_2
RAM_X2_TICKET_NUMBER = "TKTA0000000009"

DISPATCH_TABLE_RAM_X2_PLUS_MB_NIC = """Date
Ticket No#
Case ID#
Server SN
Rack Info
Faulty Part
OLD PN
NEW PN
Maker
Model
Engineer
13/7/2026
TKTA0000000009
TKTB0000000007
DSN000005
TESTDC1_F2_DHGA-A-21-17
Memory x2
PN-DEMO-0006
PN-DEMO-0006
Q
MPN-DEMO-0002
Alex | Riley Deliver onsite
13/7/2026
TKTA0000000009
TKTB0000000007
DSN000005
TESTDC1_F2_DHGA-A-21-17
Motherboard - high risk have bent pins
YZMB-02666-106
YZMB-02666-106 borrow
Q
MPN-DEMO-0002
Alex | Riley Deliver onsite
13/7/2026
TKTA0000000009
TKTB0000000007
DSN000005
TESTDC1_F2_DHGA-A-21-17
NIC
PN-DEMO-0009
PN-DEMO-0009
Q
MPN-DEMO-0002
Alex | Riley Deliver onsite"""

# Real-world case: part_type field says "HDD" but the fault device name
# (fault_part) is a real NVMe device ("nvme0n1") — the device name is the
# more reliable signal and should override the ticket's own part_type,
# since these are physically SSDs, not spinning HDDs.
NVME_LABELED_HDD_TICKET = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：SC-2400H server_product：SCH2400-D2-N48
服务器SN/Server SN：DSN000006
机柜位置/Location：TESTDC1_B1_DH3A-L-03
起始U位/ unit_no: 9
服务器厂商/manufacturer:SynthCore
部件位置/part_position:5
背板号/backplane_number:0
部件厂商/part_manufacturer:SynthCore
固件版本/firmware_version:
部件SN/part_sn:S123456
部件容量/part_size:1.92TB
部件类型/part_type:HDD
部件PN/part_pn:SC-NV1T9
fault_log_dir:None
故障明细/Fault_Detail:Disk failure
故障设备/fault_part：nvme0n1
故障类型/fault_type:Disk
故障描述/Fault Description:I/O error on nvme0n1
30天内重复报修次数/fault_30day_rt：0
"""

NVME_LABELED_HDD_TICKET_NUMBER = "TKTA0000000008"

# Regression fixture: the vendor ticket template glues a fixed Chinese
# instructional note directly onto the 部件位置/part_position value with no
# separator, e.g. "P1_C1_D0 （若报修为硬盘故障 ...）". The note must be
# stripped so it doesn't end up baked into the report's slot title.
BOILERPLATE_POSITION_TICKET = """工单标签/tags：
60天内重复报修次数/fault_60day_rt：0
主机业务属性/idc_kind：核心机房
Priority：normal
server_model：G220B-1G1BxxL server_product：SG44O0-3Z4186-S-WW
服务器SN/Server SN：DSN000010
机柜位置/Location：TESTDC2_B1_G1-V-10
起始U位/ unit_no: 21
服务器厂商/manufacturer:Maginfra
部件位置/part_position:P1_C1_D0 （若报修为硬盘故障，请以下方 部件位置(BMC) 为准）
部件厂商/part_manufacturer:SynthCore
固件版本/firmware_version:
部件SN/part_sn:S000002
部件容量/part_size:64GB
部件类型/part_type:Memory
部件PN/part_pn:M321R8GA0EB2-CWM
fault_log_dir:None
故障明细/Fault_Detail:Memory Device Disabled
故障类型/fault_type:Memory
故障描述/Fault Description:SensorName:P1_C1_D0_Status;Status:0x1080
30天内重复报修次数/fault_30day_rt：0
"""

BOILERPLATE_POSITION_TICKET_NUMBER = "TKTA0000000016"
