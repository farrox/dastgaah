import sys
from pathlib import Path
sys.path.insert(0, "analysis")
from extract_grand_5avazes import AVAZ_SOURCES

for s in AVAZ_SOURCES:
    print(f"\n--- {s['name']} ---")
    filt = s.get("filter_str")
    found = []
    for d in s["dirs"]:
        if not d.exists():
            print(f"Dir does not exist: {d}")
            continue
        for f in d.glob("*.wav"):
            if filt is None or filt.lower() in f.name.lower():
                found.append(f)
    print(f"Total matching wavs: {len(found)}")
    for f in found[:3]:
        print(f"  {f.name}")
