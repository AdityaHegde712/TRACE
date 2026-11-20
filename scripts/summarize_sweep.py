import csv
from collections import defaultdict
from pathlib import Path

csv_path = Path("artifacts/corpus_900_baselines/results.csv")
with open(csv_path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

stats = defaultdict(lambda: {"total": 0, "verify": 0, "close": 0, "fc": 0, "missed": 0})
for r in rows:
    p = r["policy_version"]
    s = stats[p]
    s["total"] += 1
    if r["action"] == "verify":
        s["verify"] += 1
    elif r["action"] == "close":
        s["close"] += 1
    if r["false_clearance"] == "True":
        s["fc"] += 1
    s["missed"] += int(r["objects_missed_at_close"])

header = ["Policy", "Total", "Verify%", "Close%", "FalseClear%", "TotalMissed", "MeanMissed"]
print(f"{header[0]:<25} {header[1]:<8} {header[2]:<10} {header[3]:<10} {header[4]:<14} {header[5]:<12} {header[6]:<10}")
print("-" * 95)
for p in sorted(stats):
    s = stats[p]
    tot = s["total"]
    row = [
        p,
        tot,
        f"{s['verify']/tot*100:.1f}%",
        f"{s['close']/tot*100:.1f}%",
        f"{s['fc']/tot*100:.1f}%",
        s["missed"],
        f"{s['missed']/tot:.3f}",
    ]
    print(f"{row[0]:<25} {row[1]:<8} {row[2]:<10} {row[3]:<10} {row[4]:<14} {row[5]:<12} {row[6]:<10}")
