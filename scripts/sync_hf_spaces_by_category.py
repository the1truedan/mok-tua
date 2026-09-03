#!/usr/bin/env python3
"""Pull curated leaderboards of public Hugging Face Spaces relevant to
mok-tua's video/audio-gen orchestration -- the HF-Spaces analogue of
ai-gateway's scripts/sync_openrouter_free_models.py.

Source: huggingface.co/spaces?category=<slug> is a real, curated,
semantically-categorized browse page -- NOT driven by the plain
/api/spaces REST endpoint (that endpoint silently ignores an unrecognized
`category=` param and falls back to a generic global-trending list; verified
2026-09-02). The category page's server-rendered HTML embeds the full
result set as JSON in a `data-props` attribute on its `SpaceList` Svelte
component (key: `spacesSemantcSearch`), already including `likes`,
`runtime.hardware`, `shortDescription`/`ai_short_description`, and
`originRepo` -- no follow-up per-Space API calls needed. This script
fetches that HTML and parses the embedded JSON directly.

No auth required (public page); an HF_TOKEN in the environment isn't used
here (this hits the HTML site, not the authenticated API) but is harmless
to have set.

Confirmed real category slugs (2026-09-02): video-generation (111),
voice-cloning (116), music-generation (117). audio-generation and
text-to-speech are NOT real slugs (0 results) -- don't add them without
re-verifying.

Writes:
  config/hf_spaces_by_category.generated.json  (full structured catalog)
  docs/HF_SPACES_CATEGORY_CATALOG_<date>.md    (human-readable, like the
    openrouter-free-models.md guide)
"""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "config" / "hf_spaces_by_category.generated.json"
OUT_MD = ROOT / "docs" / f"HF_SPACES_CATEGORY_CATALOG_{date.today().isoformat()}.md"

CATEGORIES = ["video-generation", "voice-cloning", "music-generation"]
UA = {"User-Agent": "Mozilla/5.0 (mok-tua-hf-space-sync/2.0)"}
MIN_LIKES = 2

PROPS_RE = re.compile(r'data-target="SpaceList" data-props="([^"]*)"')

# Model-family substrings already running locally on mrgpu (Wan2GP covers
# Wan/LTX/HunyuanVideo/Qwen-Image/Flux; Maestro adds LTX-2.3/Flux-2-Klein;
# ACE-Step covers music; PocketTTS/DramaBox/TTS-Story cover voice --
# see docs/operations/SESSION_HANDOFF_2026-09-02_MRGPU_PINOKIO_ROSTER_LOCKED_AND_COMFY_CRASH_LOOP.md
# and docs/operations/SESSION_HANDOFF_2026-09-02_MODEL_ROSTER_TTS_ADDITIONS.md).
LOCAL_FAMILIES = (
    "wan2", "wan-video", "wanx", "ltx-video", "ltx-2", "hunyuanvideo",
    "hunyuan-video", "qwen-image", "flux", "cogvideo", "mochi",
    "ace-step", "acestep", "pocket-tts", "pockettts", "dramabox",
)

LARGE_HARDWARE = {
    "a10g-large", "a100-large", "a100-large-x2", "a100-large-x4",
    "h100", "h100x2", "h100x4", "h100x8", "l40sx4", "l40sx8",
}


def fetch_category(slug: str) -> list[dict]:
    url = f"https://huggingface.co/spaces?category={slug}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    m = PROPS_RE.search(raw)
    if not m:
        raise RuntimeError(f"category page layout changed, SpaceList data-props not found for {slug}")
    data = json.loads(html.unescape(m.group(1)))["initialValues"]
    return data.get("spacesSemantcSearch") or data.get("spaces") or []


def classify(s: dict) -> dict:
    hay = " ".join([
        s.get("id", ""),
        s.get("title") or "",
        s.get("shortDescription") or "",
        s.get("ai_short_description") or "",
    ]).lower()
    matched = next((f for f in LOCAL_FAMILIES if f in hay), None)
    hw = ((s.get("runtime") or {}).get("hardware") or {}).get("current", "unknown")
    return {
        "congruent_with_local_roster": matched is not None,
        "matched_family": matched,
        "hardware": hw,
        "large_hardware": hw in LARGE_HARDWARE,
        "stage": (s.get("runtime") or {}).get("stage"),
    }


def main() -> int:
    by_category: dict[str, list[dict]] = {}
    for slug in CATEGORIES:
        raw_spaces = fetch_category(slug)
        entries = []
        for s in raw_spaces:
            if s.get("likes", 0) < MIN_LIKES or s.get("sdk") != "gradio":
                continue
            cls = classify(s)
            entries.append({
                "id": s["id"],
                "title": s.get("title"),
                "likes": s.get("likes", 0),
                "trending_score": s.get("trendingScore"),
                "last_modified": s.get("lastModified"),
                "url": f"https://huggingface.co/spaces/{s['id']}",
                "short_description": s.get("shortDescription") or s.get("ai_short_description"),
                "origin_repo": (s.get("originRepo") or {}).get("name"),
                **cls,
            })
        entries.sort(key=lambda e: e["likes"], reverse=True)
        by_category[slug] = entries

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://huggingface.co/spaces?category=<slug> (SSR-embedded SpaceList data, not /api/spaces)",
        "categories": CATEGORIES,
        "min_likes": MIN_LIKES,
        "by_category": by_category,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# HF Spaces category catalog — {date.today().isoformat()}",
        "",
        f"Pulled from huggingface.co's real category pages ({', '.join(CATEGORIES)}), "
        f"likes >= {MIN_LIKES}, sdk=gradio only. Regenerate: "
        "`python3 scripts/sync_hf_spaces_by_category.py` "
        "(or the current filename if unrenamed).",
    ]
    for slug in CATEGORIES:
        entries = by_category[slug]
        distinct = [e for e in entries if not e["congruent_with_local_roster"]]
        congruent = [e for e in entries if e["congruent_with_local_roster"]]
        large_hw = [e for e in entries if e["large_hardware"]]
        lines += [
            "",
            f"## {slug} ({len(entries)} total)",
            "",
            "### Distinct from local roster",
            "",
            "| Likes | Space | HW | Notes |",
            "|---|---|---|---|",
        ]
        for e in distinct[:25]:
            lines.append(f"| {e['likes']} | [{e['id']}]({e['url']}) | {e['hardware']} | {e['short_description'] or ''} |")
        lines += [
            "",
            "### Same family as local roster (comparison/fallback only)",
            "",
            "| Likes | Space | Matched family |",
            "|---|---|---|",
        ]
        for e in congruent[:15]:
            lines.append(f"| {e['likes']} | [{e['id']}]({e['url']}) | {e['matched_family']} |")
        if large_hw:
            lines += [
                "",
                f"### Running on large-GPU hardware ({', '.join(sorted(LARGE_HARDWARE))})",
                "",
                "| Likes | Space | HW |",
                "|---|---|---|",
            ]
            for e in large_hw:
                lines.append(f"| {e['likes']} | [{e['id']}]({e['url']}) | {e['hardware']} |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    total = sum(len(v) for v in by_category.values())
    print(f"wrote {OUT_JSON} ({total} entries across {len(CATEGORIES)} categories)")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
