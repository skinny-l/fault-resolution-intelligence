"""
load_gpu_faults.py — accelerator fault codes for the SC platform
family. Content lives in kb_content/gpu_faults.json.

    python -m scripts.load_gpu_faults
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiars import db, kb_content
from fiars.config import load_config


def main():
    entries = kb_content.load("gpu_faults")

    cfg = load_config()
    path = cfg["db_path"]
    db.init_db(path)
    con = db.connect(path)
    has = con.execute("SELECT 1 FROM knowledge WHERE error_code='XID_212_FALLEN_OFF_BUS'").fetchone()
    con.close()
    if has:
        print("Accelerator fault codes already loaded. Skipping.")
        return
    for e in entries:
        db.add_knowledge(path, e)
    print(f"Loaded {len(entries)} accelerator fault codes.")
    print(f"Total knowledge entries: {db.count_knowledge(path)}")


if __name__ == "__main__":
    main()
