# Hippo → Headroom prompt-context standard

Repeated reminders can be made available to both cloud and local agents before LiteLLM sends a request, but only after explicit promotion. The pre-prompt path is:

```text
user prompt → tagged Hippo recall → bounded reference block → Headroom compression → LiteLLM/provider
```

The implementation lives in `~/grokcode/integrations/context/hippo_prompt_context.py` and is called by the existing Headroom `maybe_compress_messages` hook. It is enabled in `~/grokcode/config/headroom.json` and can be disabled per process with `HIPPO_AUTO_CONTEXT=0`.

Only memories tagged `agent-context` or `repeated-reminder` are eligible. This is deliberate: arbitrary historical memories must not silently become system instructions or leak to a cloud provider. A reminder should be promoted with an explicit, reviewed Hippo command, for example:

```sh
hippo remember "Use the local gateway for fallback work; never expose secrets in logs." \
  --tag agent-context --tag repeated-reminder --pin --verified
```

The recall budget is 900 tokens, capped at four results and 5,000 characters. Headroom compresses the resulting block together with the user/system messages. The injected block is labeled as reference context, not an instruction, and carries memory IDs for auditability.

This is not a guarantee that every provider receives the block: direct vendor CLIs that bypass LiteLLM/Headroom are outside the path. Cloud and local agents must use the gateway path for consistent context. Keep PHI, secrets, clipboard dumps, and raw transcripts out of promoted memories.
