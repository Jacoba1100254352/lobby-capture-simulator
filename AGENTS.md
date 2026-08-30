# Codex Guidance

This is the implemented Lobby Capture Simulator and paper workspace: a standalone Java simulator centered on lobbying, money in politics, regulatory capture, and anti-capture reforms.

Use these commands from this directory:

- `make test`
- `make campaign`
- `make paper-artifacts-check`
- `make submission-package`

Project constraints:

- Keep `README.md`, `PROJECT_PLAN.md`, the Java implementation, and paper-facing report contracts aligned.
- Keep lobbying organizations, funders, influence channels, enforcement, and reform-defense strategy as the central actors.
- Borrow architecture concepts from the Congress Institutional Simulator only where they help scenario catalogs, metrics, campaign reports, or validation.
- Do not turn this into another legislative simulator; lobbying should remain the primary strategic system.

## Public Repository and Secret Handling

- Treat this repository and every committed file as public information.
- Never commit `.env`, `.env.*`, credentials, access tokens, private keys, signing material, restricted-source caches, emailed export URLs, or environment-specific private paths. Track only scrubbed templates such as `.env.example`, with blank or unmistakably fake values.
- Before staging or publishing, inspect `git status --short`, review the staged diff, and run a redacted secret scan when available. Confirm that ignored local credential files and private finalization reports remain ignored.
- If a real secret ever enters tracked content or Git history, stop publication, remove it from the affected history, and rotate or revoke the credential before pushing or changing visibility.

## Commit, Tag, and Release Policy

- Commit coherent, validated increments frequently: normally after each focused change passes its relevant checks and before switching to a different concern. Preserve unrelated user work and do not fold it into an unclear commit.
- Push validated commits as the normal completion step so the public repository stays current.
- Create tags less frequently, only for meaningful version, citation, submission, or compatibility milestones. An ordinary commit does not need a tag.
- Publish a release only at a milestone with aligned version metadata, release notes, verified artifacts and checksums where applicable, and passing release checks. Use a draft or prerelease for genuinely provisional milestones, a source-only release when that is the intended artifact, and a stable release only when the documented stable benchmark is met.
