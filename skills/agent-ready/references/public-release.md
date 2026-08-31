# Public Release Audit

Use this workflow before a repository crosses from a private trust boundary to public or broadly shared access. The audit itself is read-only. Changing visibility, deleting artifacts, rotating credentials, or rewriting history requires the authority appropriate to that action.

## Assumptions

- Brief public visibility can create permanent copies through clones, caches, mirrors, and indexes.
- A public Git repository exposes reachable history and every published branch or tag, not only the current working tree.
- Ignore rules do not remove tracked files or earlier versions.
- A clean secret scan is necessary but does not prove that personal, operational, proprietary, or licensed material is safe to publish.

## Choose the Publication Shape First

Prefer a fresh sanitized repository or source export when private history, branch structure, or operational artifacts have no public value. Preserve history only when its public value outweighs the additional audit and remediation risk.

Record what will be published: the selected refs, submodules, large-file objects, release assets, automation artifacts, documentation output, and any hosted preview. Anything outside that list stays private by default.

## Read-Only Inventory

Inspect before editing:

1. Tracked, untracked, ignored, generated, and unusually large files.
2. Every branch and tag intended for publication, plus objects reachable from them.
3. Commit subjects, bodies, trailers, author metadata, branch names, and tag names.
4. Submodules, large-file storage, release assets, package artifacts, and automation logs or attachments.
5. Documentation, screenshots, fixtures, examples, database exports, logs, model artifacts, notebooks, and sample payloads.

Do not copy findings into tickets, commit messages, chat, or reports. Record only a redacted category and remediation status.

## Scan and Classify

Use an established secret scanner with full-history support when available, then perform a content review for material scanners do not understand. Classify findings at least as:

- credentials or authentication material;
- personal or identifying data;
- internal topology, operational configuration, or incident evidence;
- business data, prompts, model outputs, training data, or customer-derived samples;
- proprietary or unlicensed code and assets;
- harmless test fixtures and obvious placeholders.

Do not dismiss a finding merely because the value is old or inactive. Rotation addresses credential validity; repository cleanup addresses disclosure. Both may be required.

## Remediate Safely

- For uncommitted material, remove it from the publication candidate and add an appropriate prevention rule or generated-data boundary.
- For committed credentials, rotate or revoke first. Removing the text does not invalidate it.
- For committed private data, choose between an approved history rewrite and a fresh sanitized repository. Prefer the sanitized repository when preserving history is unnecessary.
- Treat history rewriting as destructive: obtain explicit approval, preserve a recoverable copy, enumerate affected refs, coordinate with collaborators, and verify the rewritten result before any force update.
- Generalize documentation and examples. Replace real values with clearly synthetic fixtures that cannot be mistaken for production data.

## Publication Gate

Verify the exact candidate from a clean temporary clone:

- full-history scans have no unresolved findings;
- all intended refs and auxiliary artifact surfaces were reviewed;
- author and repository metadata are acceptable for public disclosure;
- project instructions, license, and contribution boundaries are present;
- verification commands pass without private dependencies;
- rendered documentation and generated output contain no private details;
- the rollback for repository visibility is understood, while acknowledging that already copied data cannot be recalled.

Block publication if any item is unknown. Report only categories, counts, and gate status; never reproduce the sensitive content.
