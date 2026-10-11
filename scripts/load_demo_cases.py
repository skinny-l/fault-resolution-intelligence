"""
load_demo_cases.py — load the synthetic resolved-case history.

    python -m scripts.load_demo_cases

Not autoloaded by server.py. The knowledge base is reference material and
belongs with the application; case history is a site's own operational
record, so it is loaded deliberately rather than on startup.

The 240 cases in kb_content/demo_cases.json exist so the ranking engine
and the paginated case browser have something realistic to work on. They
span roughly two years, skew recent, and carry a ~12% recurrence rate —
which is what makes the recency and fix-success terms in
fiars/recommend.py produce visibly different confidence scores rather
than a flat ranking. Every ticket number, serial and location in them is
invented.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiars import db, kb_content
from fiars.config import load_config


def main():
    cases = kb_content.load("demo_cases")

    cfg = load_config()
    path = cfg["db_path"]
    db.init_db(path)

    con = db.connect(path)
    has = con.execute(
        "SELECT 1 FROM case_history WHERE ticket_number='DEMO-00001'"
    ).fetchone()
    con.close()
    if has:
        print("Demo case history already loaded. Skipping.")
        return

    for c in cases:
        db.add_case(path, c)

    s = db.stats(path)
    print(f"Loaded {len(cases)} demo cases.")
    print(f"Total cases in history: {s['cases']}")


if __name__ == "__main__":
    main()
