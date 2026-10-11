"""
load_confirmed_solutions.py — load verified fault solutions into the
knowledge base. Content lives in kb_content/confirmed_solutions.json.

    python -m scripts.load_confirmed_solutions
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiars import db, kb_content
from fiars.config import load_config


def main():
    solutions = kb_content.load("confirmed_solutions")

    cfg = load_config()
    path = cfg["db_path"]
    db.init_db(path)

    existing = db.count_knowledge(path)
    if existing > 0:
        con = db.connect(path)
        has_ecc = con.execute("SELECT 1 FROM knowledge WHERE error_code='ECC_CE_THRESH'").fetchone()
        con.close()
        if has_ecc:
            print(f"Confirmed solutions already loaded ({existing} entries). Skipping.")
            return

    loaded = 0
    for s in solutions:
        db.add_knowledge(path, s)
        loaded += 1

    print(f"Loaded {loaded} confirmed solutions into knowledge base.")
    print(f"Total knowledge entries: {db.count_knowledge(path)}")


if __name__ == "__main__":
    main()
