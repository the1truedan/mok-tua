# Story elements schema (MOCK-TUA)

Use one file per project (`music_video_story_elements.md`, `anime_cartoon_story_elements.md`, or instructor fixtures).

- YAML front-matter: title, type, target_duration, fps, resolution, style_lock, character_refs, audio
- `# Scene N` blocks with id/duration/location/mood
- `## Shot N.M` blocks with prompt, camera, consistency, status, last_good_frame, output

Sample fixture follows (also under `fixtures/sample_instructor_story.md`).

---

---
title: "MANAGER Instructor Avatar – Phase 1 Overview"
type: instructor_avatar
target_duration: "0:30"
fps: 24
resolution: "1280x720"
style_lock: "clean technical documentary, soft key light, shallow depth of field"
character_refs:
  - id: instructor
    description: "Adult instructor, calm technical presence, short dark hair, dark henley"
    lora: ""
    reference_images: []
audio:
  music_bed: ""
  voiceover: true
  bpm: 92
created: 2026-07-24
version: 1.0
---

# Scene 1 – Opening Hook
id: scene_01
duration: 18s
location: "minimal dark studio with subtle blue rim light"
mood: "focused, inviting"
notes: "Public ACL-safe fixture. No PHI."

## Shot 1.1 – Wide Establishing
id: shot_01_01
duration: 4.5s
camera: "slow push-in from medium-wide"
start_frame: null
end_frame: null
character: instructor
prompt: >
  Wide shot of instructor standing in a minimal dark studio,
  soft blue rim light, looking directly at camera with calm confidence,
  clean technical documentary style, shallow depth of field
negative_prompt: "blurry, distorted face, extra limbs, text, watermark"
seed: 42
strength: 0.85
consistency:
  - character_lock: instructor
  - style_lock: global
audio_cue: "music bed starts softly"
status: pending
last_good_frame: null
output: null

## Shot 1.2 – Medium Close-up
id: shot_01_02
duration: 6s
camera: "static medium close-up"
character: instructor
prompt: >
  Medium close-up of instructor speaking calmly to camera,
  soft key light from left, subtle blue rim, clean background,
  technical documentary style
negative_prompt: "exaggerated expression, motion blur, artifacts"
seed: 43
consistency:
  - character_lock: instructor
  - continue_from: shot_01_01
audio_cue: "voiceover begins"
status: pending

## Shot 1.3 – Gesture Insert
id: shot_01_03
duration: 7.5s
camera: "slight downward tilt to hands"
character: instructor
prompt: >
  Close shot of instructor hands gesturing lightly while explaining,
  same lighting and style as previous shots
consistency:
  - character_lock: instructor
  - continue_from: shot_01_02
status: pending

# Scene 2 – Core Concept
id: scene_02
duration: 12s
location: "same studio + floating UI elements"
mood: "explanatory, precise"

## Shot 2.1 – UI Overlay Reveal
id: shot_02_01
duration: 8s
camera: "slow orbit around instructor"
character: instructor
prompt: >
  Instructor gesturing toward soft holographic UI panels showing
  local-first agent architecture, clean technical documentary style
seed: 44
consistency:
  - character_lock: instructor
status: pending

## Shot 2.2 – Closing Beat
id: shot_02_02
duration: 4s
camera: "static medium"
character: instructor
prompt: >
  Medium shot instructor nodding once and looking to camera,
  calm confident close of segment, same studio lighting
seed: 45
status: pending
