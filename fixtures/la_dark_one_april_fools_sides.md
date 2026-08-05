---
title: "LA Dark One — April Fools / Notice Day"
type: comic_storyboard
arc: arc_1_april_fools
target_duration: "0:24"
fps: 24
resolution: "1280x720"
style_lock: "funny comic strip panels, LA documentary-comedy, soft noir sitcom, no real likenesses of other people"
character_refs:
  - id: la_dark_one
    description: "IT director by day, improviser by night; stickered laptop energy; documentary-comedy lead; not photoreal celebrity"
  - id: coach
    description: "Workshop ringmaster silhouette only; long-form improv authority; never a real-person portrait; may show disdain if pimped into an unwanted musical/rhyme bit"
  - id: hr_silhouette
    description: "Anonymous HR figure silhouette"
privacy:
  qqq: private_creative
  cloud_upload: false
  redaction: "Coach essence only; no legal names; no British/Python framing; no celebrity dinners"
created: 2026-08-05
version: 0.1
---

# Scene 1 — Dual life
id: scene_01
duration: 12s
location: "DVD Empire warehouse / IT desk amalgam"
mood: "brazen, deadpan"

## Shot 1.1 — Empire establishing
id: shot_01_01
duration: 4s
camera: "wide comic panel, slight Dutch tilt optional"
character: la_dark_one
prompt: >
  Comic book panel: IT director badge and pallet-stacked media warehouse,
  Burbank industrial comedy energy, soft noir fluorescent light, funny documentary style,
  clean inked comic panel, no logos of real companies, no readable badges with real names
negative_prompt: "photoreal face of real person, readable legal names, watermark, gore"
seed: 20140401
status: pending

## Shot 1.2 — Sticker laptop
id: shot_01_02
duration: 4s
camera: "close insert on laptop lid"
character: la_dark_one
prompt: >
  Comic panel close-up of work laptop covered in homemade stickers reading
  M-W-F, M.S.W., M F'R, brazen office rebellion, sitcom framing, clean lettering
negative_prompt: "real brand trademarks, photoreal coworker faces"
seed: 20140402
status: pending

## Shot 1.3 — Workshop night
id: shot_01_03
duration: 4s
camera: "wide stage, silhouettes"
character: coach
prompt: >
  Comic panel: black-box improv stage, BLACK THURSDAY to BLACK MONDAY show energy,
  crowd as silhouettes, Coach as workshop ringmaster silhouette only (no real likeness),
  long-form improv authority, warm stage light, funny LA night
negative_prompt: "photoreal face, celebrity likeness, British costume caricature, cabaret singer"
seed: 20140403
status: pending

# Scene 2 — April Fools
id: scene_02
duration: 12s
location: "office / parking lot"
mood: "impeccable timing comedy"

## Shot 2.1 — Notice day calendar
id: shot_02_01
duration: 4s
camera: "calendar insert + hero medium"
character: la_dark_one
prompt: >
  Comic panel: wall calendar page April 1 2014 circled, hero thinking
  "Today I give notice", deadpan sitcom, soft office light
seed: 20140404
status: pending
i2v_priority: high

## Shot 2.2 — HR twist
id: shot_02_02
duration: 4s
camera: "two-shot comic panel"
character: hr_silhouette
prompt: >
  Comic panel: HR silhouette across a desk saying Actually you are free to go,
  hero stunned comedy beat, April Fools timing, clean ink, no real company logos
seed: 20140405
status: pending

## Shot 2.3 — Exit
id: shot_02_03
duration: 4s
camera: "exterior push-out"
character: la_dark_one
prompt: >
  Comic panel: hero walks into California sunlight with stickered laptop under arm,
  caption energy Impeccable timing, hopeful absurd comedy, wide panel
seed: 20140406
status: pending
i2v_priority: high

# Orchestration notes
# - Generate stills for all 6 shots first (storyboard)
# - I2V overnight on shot_02_01 and shot_02_03 (and optional shot_01_01)
# - Stitch order: 01_01 → 01_02 → 01_03 → 02_01 → 02_02 → 02_03
# - QQQ: no cloud auto-upload; social-staging draft only after human approve
