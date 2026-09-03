# HF Spaces earmarked as cloud-call tools for mok-tua — 2026-09-02

Best finds from `docs/HF_SPACES_CATEGORY_CATALOG_2026-09-02.md`, registered in `api/providers.py` under a new `kind: "hf_space"` block (11 entries) as overflow/comparison/gap-fill tools — not local launches. `launch_provider()` short-circuits `kind: "hf_space"` to `status: "cloud_hosted"` (nothing to spawn); call these via `gradio_client` against the `open` field (an `owner/space` id, resolves fine) from a `backends/*.py` module, same pattern as `ace_step.py`/`pocket_tts.py`/`dramabox.py`.

**These are not default/blocking dependencies for anything.** Treat as occasional overflow when the local roster is saturated or missing a capability, never as something an unattended orchestration run depends on.

## Real caveats, confirmed by live-testing 4 of the 11 this pass — not theoretical

| Space | Checked | Result |
|---|---|---|
| `YatharthS/LuxTTS` | ✅ | **Down** — `gradio_client` raised `RUNTIME_ERROR` (owner-side crash) |
| `coqui/xtts` | ✅ | **Down** — same `RUNTIME_ERROR`. Plausible cause: Coqui AI (the company) ceased operations |
| `myshell-ai/OpenVoiceV2` | ✅ | Up, but its legacy `fn_index`/websocket-queue API is **incompatible with current gradio_client** (2.6.0 → `Unknown protocol: ws`) |
| `facebook/MusicGen` | ✅ | Up, modern named-endpoint API confirmed, but a test call errored (`AppError: Internal Gradio error`) — the "required" `melodies` Audio param likely can't actually be omitted despite the signature; needs a real reference clip to retry |
| the other 7 | ❌ not checked | registered only, unverified |

**Takeaway: 2 of 4 tested were unusable outright, a 3rd needs extra client-version handling.** This is exactly why every entry's `note` says "not yet call-verified" and none are wired into any default launch chain — verify immediately before depending on any of these for real work, don't assume the registry entry means it's ready.

## The 11 registered

| Provider id | Space | Why it matters | Status |
|---|---|---|---|
| `hf_luxtts` | `YatharthS/LuxTTS` | Would-be workaround for the local LuxTTS install, permanently blocked by a Rust/tokenizers upstream deadlock (see `docs/operations/SESSION_HANDOFF_2026-09-02_MODEL_ROSTER_TTS_ADDITIONS.md`) | 🔴 Space down |
| `hf_xtts` | `coqui/xtts` | Real TTS/voice-clone gap vs. local roster, 2766 likes | 🔴 Space down |
| `hf_openvoice` | `myshell-ai/OpenVoiceV2` | Distinct voice-clone architecture, real gap | 🟡 up, client-incompatible |
| `hf_rvc` | `r3gm/rvc_zero` | Voice **conversion** (not TTS) — a capability the local roster has none of | ⚪ unverified |
| `hf_musicgen` | `facebook/MusicGen` | Distinct from local ACE-Step, official Meta space, 5088 likes | 🟡 up, test call failed |
| `hf_stable_audio` | `stabilityai/stable-audio-3` | Official Stability music/SFX-from-text | ⚪ unverified |
| `hf_liveportrait` | `KlingTeam/LivePortrait` | Portrait motion-transfer, distinct from local DreamTalk, 3785 likes | ⚪ unverified |
| `hf_sadtalker` | `vinthony/SadTalker` | Talking-face video, distinct architecture from DreamTalk | ⚪ unverified |
| `hf_magicanimate` | `zcxu-eric/magicanimate` | Animated video from images + motion sequence | ⚪ unverified |
| `hf_latentsync` | `fffiloni/LatentSync` | Audio-conditioned lipsync — complements FaceFusion's lipsync, doesn't duplicate it | ⚪ unverified |
| `hf_minimax_h3` | `MiniMaxAI/MiniMax-H3-Turbo-Lora` | Official-source comparison point for the same H3 tech Maestro's local H3 Sol Engine already runs | ⚪ unverified |

## Next steps (not done this pass)

1. Verify the remaining 7 the same way PocketTTS/DramaBox were verified locally: introspect via `view_api()`, run one real call, only then write a `backends/*.py` module.
2. For `hf_musicgen`: retry with a real short reference clip instead of `melodies=None`.
3. For `hf_openvoice`: either pin an older `gradio_client` that still speaks the legacy ws-queue protocol, or call its HTTP API directly.
4. For `hf_luxtts`/`hf_xtts`: periodically re-check — both may come back, or may need replacing with a different hosting Space for the same model.
