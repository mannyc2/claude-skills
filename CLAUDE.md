# Claude Skills Marketplace

## Versioning

A GitHub Action auto-bumps `.claude-plugin/marketplace.json` version on push to main based on conventional commit prefixes:

- `feat:` → minor bump
- `fix:` → patch bump
- `BREAKING CHANGE` or `!:` → major bump
- Anything else → no bump

Don't manually edit the version. Just use the right commit prefix.
