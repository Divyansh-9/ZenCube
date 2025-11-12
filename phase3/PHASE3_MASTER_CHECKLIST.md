# Phase 3 Master Checklist

## Task Tracking
- [~] File System Restriction (dev-safe) — 🔄 In-Progress (started by GitHub Copilot 2025-11-12 10:30 UTC)

## Filesystem Isolation Goals
- [ ] Implement chroot() jail for sandboxed processes
- [ ] Provide read-only filesystem mount support
- [ ] Configure mount namespaces via unshare(CLONE_NEWNS)
- [ ] Isolate temporary directories (per-sandbox /tmp)
- [ ] Define directory whitelisting and blacklisting rules
- [ ] Add dedicated filesystem isolation test programs

## Hardening Enhancements
- [ ] Introduce seccomp-based system call filtering
- [ ] Enable network namespace isolation where applicable
- [ ] Implement capability dropping for reduced privileges
