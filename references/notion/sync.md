# Notion Material Sync

This file defines how Easy Apply mirrors local application PDFs into the Notion `Submitted Materials` property.

Local generated files are the source of truth. Sync updates files only; it must not modify application Status or any other Job Tracker property.

Material sync is available only when `notion.enabled` is true. When it is false, do not call Notion or upload files; report that local materials remain valid and remote sync was skipped.

## 1. Input

Sync requires:

```text
workspace path
notion.enabled = true
Notion row/page identifier
persisted File Slug
```

Never reconstruct `file_slug` from Company or Position during sync.

## 2. Find the complete local material set

Run `scripts/find_materials.py` for the persisted slug.

Recognized current PDFs are:

```text
artefacts/resume-pdf/resume-<file_slug>.pdf
artefacts/cover-letter-pdf/cover-letter-<file_slug>.pdf
```

The cover letter is optional. At least one current PDF must exist before sync proceeds.

Do not read `artefacts/archive/` and do not upload `.tex` sources to Submitted Materials.

## 3. Create and complete uploads

For each current PDF, one at a time:

1. ask the Notion connector/API for a file-upload slot using the exact local filename;
2. receive the upload identifier, upload URL, and required upload headers;
3. immediately upload that file with `scripts/upload_file.py`;
4. retain the successful Notion file-upload identifier;
5. only then create the next upload slot.

Upload URLs may expire. Do not create a large batch of upload slots and postpone the actual HTTP uploads.

Do not log upload URLs, authorization headers, cookies, or connector credentials into workspace state.

## 4. Atomic property replacement

`Submitted Materials` is a complete list, not an append-only field.

After **all** current local PDFs upload successfully, update the Notion row once with the full new list of file-upload references.

Example local state:

```text
resume-acme-support-engineer.pdf
cover-letter-acme-support-engineer.pdf
```

The replacement list must contain both files.

If the resume was previously synced and a cover letter is generated later, re-upload the current resume and the new cover letter, then replace the property with both. This keeps Notion equal to the local current set and avoids depending on stale remote upload references.

## 5. Failure behavior

If any step fails:

- do not replace `Submitted Materials` with a partial list;
- do not change Status;
- record/report which stage failed;
- keep the valid local files unchanged;
- a later sync may retry from the local material set.

A failed upload slot should be treated as disposable; request a new slot on retry rather than assuming an old URL is still valid.

## 6. Ownership

Sync may write only:

```text
Submitted Materials
```

It must not write:

```text
Status
Apply date
Priority
Cover Letter
Appendix
Position
Company
Location
URL
File Slug
```

## 7. Trigger points

Run sync after:

- a resume PDF is generated successfully;
- a cover-letter PDF is generated successfully;
- the user explicitly asks to resync modified local materials.

Do not automatically regenerate materials merely because sync is requested.

## 8. Verification

A successful sync should verify, through the connector response when available, that:

- the page update succeeded;
- the number of Submitted Materials entries equals the number of current local PDFs;
- filenames correspond to the current local set.

If remote verification is unavailable, report that the update request succeeded but could not be independently reread.

## 9. Run logging

When the runtime maintains `state/runs/`, record only operational metadata such as:

```text
file_slug
local filenames
sync start/end time
success/failure
failed stage when applicable
```

Never persist temporary upload URLs or authorization headers.
