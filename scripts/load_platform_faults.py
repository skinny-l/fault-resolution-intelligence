"""
load_platform_faults.py — SC platform-family specific fault codes.
SMART attributes, population-order quirks, slot-lane constraints and
accelerator power notes. Deduplicates against existing knowledge
entries. Content lives in kb_content/platform_faults.json.

    python -m scripts.load_platform_faults
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiars import db, kb_content
from fiars.config import load_config


def main():
    entries = kb_content.load("platform_faults")

    cfg = load_config()
    path = cfg["db_path"]
    db.init_db(path)

    con = db.connect(path)
    has = con.execute("SELECT 1 FROM knowledge WHERE error_code='SC_DIMM_POP_ORDER'").fetchone()
    con.close()
    if has:
        print("Platform fault codes already loaded. Skipping.")
        return

    for e in entries:
        db.add_knowledge(path, e)
    print(f"Loaded {len(entries)} platform-specific fault codes.")
    print(f"Total knowledge entries: {db.count_knowledge(path)}")


if __name__ == "__main__":
    main()
