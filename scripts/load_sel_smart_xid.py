"""
load_sel_smart_xid.py — legacy loader for the SEL / SMART / Xid subset
of the reference data. Superseded by load_reference_data.py, which loads
the same records plus the inter-socket link faults; the two share a
dedup sentinel, so whichever runs first wins and the other skips.
Content lives in kb_content/sel_smart_xid.json.

    python -m scripts.load_sel_smart_xid
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiars import db, kb_content
from fiars.config import load_config


def main():
    entries = kb_content.load("sel_smart_xid")

    cfg = load_config()
    path = cfg["db_path"]
    db.init_db(path)
    con = db.connect(path)
    has = con.execute("SELECT 1 FROM knowledge WHERE error_code='SEL_0x04'").fetchone()
    con.close()
    if has:
        print("SEL/SMART/Xid data already loaded. Skipping.")
        return
    for e in entries:
        db.add_knowledge(path, e)
    print(f"Loaded {len(entries)} SEL/SMART/Xid/CPU entries.")
    print(f"Total knowledge entries: {db.count_knowledge(path)}")


if __name__ == "__main__":
    main()
