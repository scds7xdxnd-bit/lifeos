# DevOps Handoff: CI Pipeline Fix Required

**Date**: 2024-12-07  
**From**: LifeOS Architect  
**To**: DevOps Team  
**Priority**: High  
**Branch**: `test/ci-pipeline`

---

## Background: What We're Trying to Accomplish

### The Goal

We are setting up a **complete CI/CD pipeline** for the LifeOS monorepo to enable:

1. **Automated Quality Gates** — Every pull request automatically runs linting (flake8), type checking, and tests before merge is allowed
2. **Docker Validation** — Ensure our Docker Compose configurations are valid before deployment
3. **Continuous Deployment** — Once merged to `main`, automatically build and deploy to staging/production
4. **Release Management** — Tag-based releases with proper versioning

### Why This Matters

Before this CI/CD setup, deployments were manual and error-prone. The pipeline ensures:
- No broken code reaches production
- Consistent environments via Docker
- Automated testing catches regressions early
- Clear deployment process for the team

### What We've Done So Far

| Step | Status | Description |
|------|--------|-------------|
| 1. CI/CD Architecture Design | ✅ Complete | Created `CI_CD_ARCHITECTURE.md` with full specs |
| 2. GitHub Actions Workflows | ✅ Complete | 4 workflows: PR, main, release, nightly |
| 3. Push to GitHub | ✅ Complete | Repository at `origin/main` |
| 4. Test Branch Created | ✅ Complete | `test/ci-pipeline` to validate CI before merge |
| 5. Fix flake8 Errors | ✅ Complete | Added TYPE_CHECKING imports for forward refs |
| 6. Fix docker-compose v2 | ✅ Complete | Changed `docker-compose` → `docker compose` |
| 7. Remove obsolete version | ✅ Complete | Removed `version: "3.9"` from compose files |
| 8. Fix compose merge issue | ❌ **BLOCKED** | Duplicate `device_cgroup_rules` — **THIS TICKET** |

### The Current Blocker

The CI pipeline validates that Docker Compose files are syntactically correct. When we validate the monitoring override file merged with the base file, Docker Compose concatenates arrays — causing duplicate entries in `device_cgroup_rules`.

Once this is fixed, the CI pipeline will be fully operational.

---

## Issue Summary

The CI pipeline is failing on the `compose-validate` job due to a Docker Compose merge conflict between `docker-compose.yml` and `docker-compose.monitoring.yml`.

## Error Message

```
validating /home/runner/work/lifeos/lifeos/docker-compose.monitoring.yml: 
services.cadvisor.device_cgroup_rules items at 0 and 1 are equal
```

## Root Cause

Both `docker-compose.yml` and `docker-compose.monitoring.yml` define the `cadvisor` service with identical `device_cgroup_rules`:

```yaml
device_cgroup_rules:
  - 'rule_type=allow major=*'
```

When Docker Compose merges these files (`-f docker-compose.yml -f docker-compose.monitoring.yml`), it **concatenates arrays**, resulting in duplicate entries — which is invalid.

## Affected Files

| File | Line | Issue |
|------|------|-------|
| `docker-compose.yml` | ~line 95 | Base cadvisor definition with `device_cgroup_rules` |
| `docker-compose.monitoring.yml` | ~line 138 | Override cadvisor also declares `device_cgroup_rules` |

## Recommended Fix

**Option A (Preferred)**: Remove `device_cgroup_rules` from `docker-compose.monitoring.yml`

The monitoring file is an override — it should only add/modify what's different from the base. Since the base already has the correct `device_cgroup_rules`, the override should not re-declare it.

```yaml
# docker-compose.monitoring.yml - cadvisor service
# REMOVE this block:
device_cgroup_rules:
  - 'rule_type=allow major=*'
```

**Option B**: Remove cadvisor from base file entirely

If cadvisor is only needed for monitoring, move the entire service definition to `docker-compose.monitoring.yml` only.

## Verification

After fix, run locally:

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml config > /dev/null && echo "✓ Valid"
```

## CI Workflow Reference

The failing job is in `.github/workflows/ci.yml`:

```yaml
- name: Validate docker-compose.monitoring.yml (as override)
  run: |
    docker compose -f docker-compose.yml -f docker-compose.monitoring.yml config > /dev/null
    echo "✓ docker-compose.monitoring.yml is valid (as override)"
```

## Previous Fixes Applied (for context)

1. ✅ Fixed flake8 F821 errors (TYPE_CHECKING imports)
2. ✅ Changed `docker-compose` → `docker compose` (v2 syntax)
3. ✅ Removed obsolete `version: "3.9"` from compose files
4. ❌ **This issue** — duplicate `device_cgroup_rules` on merge

---

**Action Required**: DevOps team to implement fix and push to `test/ci-pipeline` branch.
