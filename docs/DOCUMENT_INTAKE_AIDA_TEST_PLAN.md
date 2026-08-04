# Scanner drop → A.I.D.A. intake test plan

This is a small, privacy-safe test lane for receipts, letters, and forms. Real
care documents remain local and are never committed to this repository.

## Staging

```bash
export MOK_TUA_DOCUMENT_WORK_ROOT="$PWD/work/document-intake"
./scripts/stage_scanned_document_drop.sh /path/to/scanner/drop
```

The harness copies JPG/JPEG/PNG/PDF files into `incoming/`, preserves originals,
hashes every staged file, quarantines duplicate filenames, and writes a JSONL
manifest. It does not OCR, call a model, or publish anything.

## Test progression

1. **Drop evidence:** verify the manifest, SHA-256, byte count, source filename,
   and operator scope.
2. **Normalize:** rotate/deskew/crop a copy only; retain the original hash and
   record the tool/version.
3. **A.I.D.A. PDF lane:** route a synthetic receipt, synthetic letter, and
   blank form to the configured A.I.D.A. endpoint. Record request/response
   hashes, route, model, and failure/quarantine status; never put full PHI in
   logs.
4. **Form lane:** inspect extracted fields against a hand-labeled fixture;
   preserve confidence and “needs human review” for ambiguous fields.
5. **Context catalog:** append a privacy-safe record to
   `catalog/context_receipts.jsonl` linking source hash, document class,
   extracted entities, consent class, and the C.H.A.I.N.S. receipt ID.
6. **Human review:** approve, correct, reject, or quarantine. No downstream
   caregiving module consumes unreviewed extraction.
7. **Re-run:** process the same hash twice and confirm idempotent output.

## M.A.N.A.G.E.R. module handoff

The catalog is an evidence index, not a medical record. It should support the
M.A.N.A.G.E.R. intake, compliance, resource, and audit modules while keeping
raw scans in the private work root. Export only synthetic fixtures and
redacted manifests for GitHub examples.

## Exit criteria

- original and derived hashes are linked;
- unsupported, suspicious, or oversized files quarantine safely;
- A.I.D.A. route and model are explicit;
- form fields retain confidence and review state;
- catalog and C.H.A.I.N.S. receipt are reproducible;
- no raw document, PHI, credential, or home path enters Git.
