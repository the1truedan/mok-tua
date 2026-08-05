# Pinokio gamut smoke — mok-tua public packet (2026-08-05)

**Purpose:** Evidence that the Pinokio / conductor tool mesh works across the full intended gamut — bounded probes only (no NFS deep-walk, no dirty force-pull).  
**Machine packet:** `docs/reports/public_release_packet_2026-08-05.json`  
**Earmark:** 16:20 CDT public flip (human go)

---

## 1. Privacy / protect-branch rescan

| Gate | Result |
|------|--------|
| Remotes userinfo | **Clean** |
| Secrets in tree | **None** (env names only) |
| PHI bodies | **None** |
| LAN / `/Users/*` in tracked tree | **Scrubbed** → `gpu-host` / `control-host` / `desk-host` |
| `.hippo/` | **Gitignored** |
| Branch protection on free private | **403** — enable **after** public (see `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`) |

---

## 2. Live HTTP matrix (gpu / desk roles)

Probes use the operator lab; public docs only name **roles**.

| Service | Role label | HTTP | Notes |
|---------|------------|------|-------|
| Pinokio control plane | desk-host / loopback `:42000` | **200** | pterm resolvable |
| ComfyUI `system_stats` | gpu-host `:8188` | **200** | stills path |
| Maestro | gpu-host `:7860` | **200** | LAN share live |
| FaceFusion | gpu-host `:7870` | **200** | ORT CUDA host env |
| Director's Console UI | gpu-host `:5173` | **200** | |
| Director's CPE | gpu-host `:9800` | **200** | |
| Director's orch | gpu-host `:9820` | **404** | port up path odd; UI/CPE green |
| Wan Gradio family | gpu-host `:7861–7865` | **down** | **honest skip** (overnight E8 same) |

---

## 3. pterm search gamut (desk Pinokio index)

`pterm` resolved from `~/pinokio/bin/npm/bin`. Search hits (installed wrappers; many show `offline` on **desk** while **gpu-host** HTTP is live — expected host split):

| Query | Top apps found |
|-------|----------------|
| comfy | ComfyUI, Phosphene, ACE-Step, Wan2GP |
| facefusion | FaceFusion |
| maestro | Maestro.git, Maestro |
| director | Director's Console, Maestro, Phosphene |
| wan | wan.git / Wan2GP family |
| tts / ace-step | TTS-Story, ACE-Step family |
| freemocap / cogstudio / dreamtalk | present in catalog |

Affinity catalog (51 apps): control-repo `data/catalog/pinokio_api_host_affinity_2026-08-05.json`  
Counts: mac_metal 5 · gpu-host_cuda 12 · either 22 · deferred 12.

---

## 4. Creative smoke already on disk

| Evidence | Status |
|----------|--------|
| Overnight E0–E16 scorecard | ok / partial with documented skips |
| M.A.N.A.G.E.R. updates comic (5 panels + FF strip) | ok |
| Hybrid vibe demo **14.58 s** | ok (Grok I2V ×2 + kenburns finale) |
| Local kenburns demo **12.50 s** | ok |

---

## 5. mok-tua unit tests

```text
Ran 12 tests — OK
```

---

## 6. Known skips (do not greenwash)

1. Wan I2V ports not listening at probe time  
2. Director orch `:9820` → 404  
3. Grok Imagine video rate limit on third segment  
4. Desk `pterm status` offline for apps that run on gpu-host host-env (Maestro/FaceFusion)  
5. Mac-only apps (phosphene, mlx-*, agentsviewMAC) — policy skip on Linux runtime  

---

## 7. 16:20 flip checklist

- [x] Scrub tracked LAN/home paths  
- [x] `.hippo` ignore  
- [x] Protect-branch runbook written  
- [x] Demo video dual path  
- [x] Gamut smoke report  
- [ ] Human: review + `gh repo edit --visibility public`  
- [ ] Human: enable `main` protection immediately after  
- [ ] Optional: GH Release + attach hybrid mp4  

*Agents do not flip visibility unattended.*
