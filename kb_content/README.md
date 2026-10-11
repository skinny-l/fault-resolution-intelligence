# kb_content/

The knowledge-base content the `scripts/load_*.py` loaders insert into
`fiars.db`.

**Everything in this directory is synthetic.** The hardware, the error
codes, the rail names, the serial numbers and the case history are all
invented. They describe a fictional server platform family built for
this repository — see `scripts/synthetic_spec.py` for what was made up
and what was deliberately kept real.

These files are committed, unlike the rest of the repository's generated
state, because the application is meant to work on a fresh clone with no
setup: clone, run `python server.py`, and a populated knowledge base is
already there to search against.

## Regenerating

    python -m scripts.generate_synthetic_kb

Deterministic — the same seed produces byte-identical output. Delete
everything here except this file, regenerate, and `git diff` should come
back empty. That is the check that the committed dataset really is the
generated one.

## Files

| File | Records | Loader |
|---|---|---|
| `confirmed_solutions.json` | 17 | `scripts/load_confirmed_solutions.py` |
| `server_fault_kb.json` | 29 | `scripts/load_server_fault_kb.py` |
| `platform_faults.json` | 14 | `scripts/load_platform_faults.py` |
| `gpu_faults.json` | 10 | `scripts/load_gpu_faults.py` |
| `reference_data.json` | 37 | `scripts/load_reference_data.py` |
| `sel_smart_xid.json` | 30 | `scripts/load_sel_smart_xid.py` (legacy) |
| `power_fault_article.json` | 1 article / 36 patterns | `scripts/load_kb_power_fault.py` |
| `demo_cases.json` | 240 | `scripts/load_demo_cases.py` |

The first five files total 107 knowledge entries. `sel_smart_xid.json`
is the SEL/SMART/Xid subset of `reference_data.json`, loaded by a legacy
loader that shares a dedup sentinel with the reference loader — whichever
runs first wins and the other skips.

## Entry format

Each "list of entries" file is a JSON array of objects shaped like:

```json
{
  "category": "Memory",
  "error_code": "ECC_CE_THRESH",
  "fault_description": "...",
  "affected_parts": "...",
  "root_cause": "...",
  "solution": "...",
  "source": "..."
}
```

`power_fault_article.json` is a single object with `title`, `scope`,
`problem`, `solution`, `root_cause`, `suggestions`, `source_url`, and
`error_map` — a list of `{error_pattern, power_rail, suspect_components,
dimm_slots, remark?}` objects that `fiars/recommend.py` matches raw
ticket text against.

`demo_cases.json` is a list of resolved cases in the shape
`fiars.db.add_case()` expects. These exist so that the similarity ×
recency × fix-success ranking and the server-side pagination have
realistic data to work on — an empty case table makes both features
untestable.

## Loading

The server autoloads the knowledge base and the power-fault article on
startup. The case history is loaded separately, on purpose, so the
knowledge base and the case history can be populated independently:

    python -m scripts.load_demo_cases

Each loader checks for existing entries first and skips if already
loaded, so re-running is safe.

## Replacing this with real data

Swap the JSON files. No Python changes are needed — that is why the
content lives out here rather than in the loaders. A deployment with its
own fault history writes its records into files of the same shape and
runs the same loaders.
