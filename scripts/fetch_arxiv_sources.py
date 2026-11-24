"""
Downloads primary source LaTeX/text from arXiv e-print endpoints into docs/research/sources/
"""
from __future__ import annotations

import io
import gzip
import tarfile
import urllib.request
from pathlib import Path

PAPERS = {
    "Where2comm_2209.12836": "2209.12836",
    "OPV2V_2109.07644": "2109.07644",
    "V2V4Real_2303.07601": "2303.07601",
    "QUEST_2308.01633": "2308.01633",
    "V2X-ViT_2203.10638": "2203.10638",
    "CoBEVT_2207.02202": "2207.02202",
    "CoAlign_2211.07214": "2211.07214",
    "SyncNet_2207.08560": "2207.08560",
    "DAIR-V2X_2204.05575": "2204.05575",
    "V2VNet_2008.07519": "2008.07519",
    "When2com_2006.00176": "2006.00176",
    "Who2com_2003.04944": "2003.04944",
}

DEST_DIR = Path("docs/research/sources")
DEST_DIR.mkdir(parents=True, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for name, arxiv_id in PAPERS.items():
    out_dir = DEST_DIR / name
    if out_dir.exists() and any(out_dir.glob("*.tex")):
        print(f"Skipping {name}, already downloaded.")
        continue

    out_dir.mkdir(parents=True, exist_ok=True)
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    print(f"Fetching {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        # Try tar.gz
        try:
            with tarfile.open(fileobj=io.BytesIO(data)) as tar:
                for member in tar.getmembers():
                    if member.name.endswith((".tex", ".bbl", ".txt", ".md")):
                        # Avoid path traversal
                        target_path = out_dir / Path(member.name).name
                        f = tar.extractfile(member)
                        if f:
                            target_path.write_bytes(f.read())
            print(f"  Extracted tar for {name} ({len(list(out_dir.glob('*')))} files)")
            continue
        except Exception:
            pass

        # Try gzip single file
        try:
            decompressed = gzip.decompress(data)
            (out_dir / "main.tex").write_bytes(decompressed)
            print(f"  Extracted gzip single file for {name}")
            continue
        except Exception:
            pass

        # If plain text/tex
        if b"\\documentclass" in data or b"\\begin{document}" in data:
            (out_dir / "main.tex").write_bytes(data)
            print(f"  Saved raw tex for {name}")
            continue

        print(f"  Warning: Unknown format for {name} ({len(data)} bytes)")
    except Exception as e:
        print(f"  Error fetching {name}: {e}")

print("Done fetching sources.")
