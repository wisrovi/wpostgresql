# LTS Policy

## Long Term Support Commitment

wpostgresql is committed to providing stable and reliable versions for production use. This document outlines our LTS release schedule and support policy.

---

## LTS Releases

| Version | Release Date | End of Support | Status |
|---------|-------------|----------------|--------|
| 1.0.0   | 2026-03-31  | 2028-03-31     | ✅ LTS |

---

## Support Timeline

- **LTS Duration**: 24 months from release date
- **Support Type**: Security patches, critical bug fixes only
- **No New Features**: LTS releases receive no new features

---

## Release Schedule

### Minor Releases (Every 6 months)
- New features
- Performance improvements
- Non-breaking API changes

### Patch Releases (As needed)
- Security fixes
- Critical bug fixes
- Dependency updates

### Major Releases
- Breaking changes
- Major architectural changes

---

## What is Supported

### During LTS
- ✅ Security patches
- ✅ Critical bug fixes
- ✅ Dependency compatibility fixes
- ❌ New features

### After LTS End
- ❌ No security updates
- ❌ No bug fixes
- ❌ No support

---

## Backward Compatibility

We are committed to maintaining backward compatibility within major versions:

- **Major version (1.x)**: May include breaking changes
- **Minor version (1.0.x)**: No breaking changes, only additive features
- **Patch version (1.0.1)**: Only bug fixes, no API changes

---

## Migration Path

When a new major version is released, we will provide:
- Migration guide in CHANGELOG.md
- Deprecation warnings in library output
- Minimum 6 months deprecation period

---

## Reporting Issues

For LTS versions, we prioritize:
1. Security vulnerabilities
2. Data corruption bugs
3. Critical runtime errors

Report issues at: https://github.com/wisrovi/wpostgresql/issues

---

## Version Skipping

We may skip versions if:
- Critical security issues require immediate major bump
- Major architectural changes necessitate breaking changes

---

This policy is effective as of 2026-03-31.