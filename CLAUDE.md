# CLAUDE.md: AFI Academy plugin marketplace (`afi-academy-plugin`)

Public Claude Code marketplace with one plugin, `afi-academy` (the `/afi-course` skill and the AFI Academy connector).
Public on purpose, so course authors need no GitHub access. It must stay free of secrets and company data.

## Rules for agents working in this repo

- **`plugins/afi-academy/` and `.claude-plugin/marketplace.json` are generated. Don't edit them here.** The source
  is the afi-lms repo: `skills/afi-course/` and `connector/`. Rebuild with `uv run scripts/build_plugin.py <this
  checkout>` from afi-lms, then commit here on a branch and open a PR.
- **Versions:** the plugin version is afi-lms `connector/pyproject.toml`. Claude Code only updates installed plugins
  when the version changes, so the build refuses changed content at an unchanged version. Never reuse a version.
  Add a dated entry to `CHANGELOG.md` for each release; tag `vafi-academy-<version>`.
- **Nothing private, ever:** no keys or tokens, no customer or employee data, no internal URLs. Each author's key lives
  in their own `~/.afi-academy/connector.env`, saved from the Academy's Connect Claude page.
- Work on a branch, merge via PR. Don't push or merge unless Dan asks.
