"""
Download two sample MP4s into frontend/public/videos/ as matrices.mp4 and factorials.mp4
so the Video page serves local files after the API wait.

Run from repo root:  python scripts/fetch_lesson_videos.py
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "frontend" / "public" / "videos"

SOURCES = {
    "matrices.mp4": "https://www.w3schools.com/html/mov_bbb.mp4",
    "factorials.mp4": "https://samplelib.com/preview/mp4/sample-10s.mp4",
}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        out = DEST / name
        print(f"Fetching {url} -> {out}")
        urllib.request.urlretrieve(url, out)  # noqa: S310 (intentional sample URLs)
        print(f"  wrote {out.stat().st_size} bytes")
    print("Done. Restart the FastAPI process so video_mock_payload picks up the new files.")


if __name__ == "__main__":
    main()
