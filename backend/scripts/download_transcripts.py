"""Script to download curated Lenny's Podcast transcripts from the public archive."""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Curated seminal episodes covering core Growth, PLG, Metrics, and Product Leadership topics
DEFAULT_EPISODES = [
    "adam-fishman",
    "elena-verna",
    "brian-balfour",
    "casey-winters",
    "shreyas-doshi",
    "hila-qu",
    "fareed-mosavat",
    "ethan-evans",
]

BASE_URL = "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/episodes/{slug}/transcript.md"
TARGET_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"


def download_transcript(slug: str, target_dir: Path) -> bool:
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / f"{slug}.md"

    if out_file.exists() and out_file.stat().st_size > 500:
        print(f"[CACHE] {slug} already downloaded at {out_file.name}")
        return True

    url = BASE_URL.format(slug=slug)
    print(f"[FETCH] Downloading {slug} from {url}...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LennyGrowthAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[SUCCESS] Saved {slug} ({len(content):,} characters)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download {slug}: {e}")
        return False


def main():
    print("=== Downloading Lenny's Podcast Transcripts ===")
    episodes = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_EPISODES
    success_count = 0

    for slug in episodes:
        if download_transcript(slug, TARGET_DIR):
            success_count += 1

    print(f"\n[SUMMARY] Successfully processed {success_count}/{len(episodes)} episodes.")
    print(f"[DIR] Transcripts directory: {TARGET_DIR}")


if __name__ == "__main__":
    main()
