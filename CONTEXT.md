# MOCK-TUA context

## Source chat

| Field | Value |
|-------|--------|
| Share | https://grok.com/share/c2hhcmQtNA_63f7803d-ec53-45fa-8a80-636deae38976 |
| Conversation | `db21c4a0-8c71-4d40-8376-f67da47a954b` |
| Title | Modular recon ranking for M.A.N.A.G.E.R. agent deck |
| Local export | `context/mock-tua.md`, `context/mock-tua.json` |

## Share-fetch rule (agents)

**Never** scrape the grok.com SPA HTML for share bodies.

```bash
cd ~/grokcode
python3 scripts/batch_share_ingest.py --url 'https://grok.com/share/c2hhcmQtNA_<uuid>'
# → vault zzz_ingest/incoming MD + grok-FULL JSON
# API: GET https://grok.com/rest/app-chat/share_links_data/{shareLinkId}
```

If a local export already exists (Downloads or `context/`), prefer that and skip re-fetch.

## Related production SSOT

- `~/grokcode/config/comfy_story_orchestration.json`
- `~/grokcode/integrations/comfyui/`
- `~/grokcode/deploy/comfyui/`
- Work I/O: `/Volumes/ai-data/work/story-anim/`
