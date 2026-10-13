---
name: amdserver-access
description: Access the user's AMD intranet server (amdserver, wyaamd-server001, 172.16.10.68) over existing SSH; locate research datasets including BvD Orbis, inspect jobs, and transfer task-authorized files. Use for requests about this specific server, not unrelated servers or local-only analysis.
---

# AMD Server Access

Use the user's existing SSH access. This skill records connection knowledge, not credentials or blanket permission to run research jobs.

## Verified connection

Last verified: 2026-10-13 from the user's Windows desktop.

| Setting | Value |
|---|---|
| SSH destination | `user@172.16.10.68` |
| Port | `22` |
| Expected hostname | `wyaamd-server001` |
| Remote home | `/home/user` |
| Local shell | Latest installed `pwsh`, with `login:false` when using the execution tool |
| Authentication | Existing local SSH configuration/key/agent resolution; no explicit key override was needed |

The specific key or agent responsible for authentication has not been established. Do not invent a key filename or read private keys to identify it. A different execution host needs its own authorized authentication and route to this private IP; this skill does not supply either.

Start with this small read-only check:

```powershell
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 user@172.16.10.68 'hostname'
if ($LASTEXITCODE -ne 0) { throw 'AMD server connection failed; inspect access before continuing.' }
```

Require the expected hostname before substantive work. If network execution needs approval, use the execution tool's normal approval mechanism. Do not weaken sandbox or SSH verification to connect.

## Remote execution from PowerShell

Send a small Python program over standard input to avoid nested Windows/Linux quoting problems. `/usr/bin/python3` was verified for standard-library inspection; it is not the research package environment.

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$code = @'
from pathlib import Path
import json, os
p = Path('/data/disk1/database/wrds/bvd/bvdorbis')
print(json.dumps({'hostname': os.uname().nodename, 'path': str(p), 'exists': p.is_dir()}))
if p.is_dir():
    for q in sorted(p.iterdir()):
        print(q.name, q.stat().st_size if q.is_file() else 'directory')
'@
$code | ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 user@172.16.10.68 '/usr/bin/python3 -B -'
if ($LASTEXITCODE -ne 0) { throw 'Read-only remote inspection failed.' }
```

For dataset locations and the existing BGD research runtime, read [references/locations.md](references/locations.md). Recheck paths before use; the recorded date is not a claim that a dataset is the latest release.

## Transfers and research work

- Use `scp -q -o BatchMode=yes -o StrictHostKeyChecking=yes` with an explicit source and destination. On Windows quote local paths, using forward slashes where helpful. Remote paths use POSIX syntax.
- Before uploading, check whether the destination exists; preserve prior files and use a new run/version or compare hashes. Before large transfers, check size and free space on both ends. Verify SHA256 after transfer (`Get-FileHash` locally; Python `hashlib` or `sha256sum` remotely).
- Copy only task-required documents, code, configuration, or result slices. Keep large databases and complete model/sample-key archives on the server unless the user requests otherwise.
- For BGD work, prefer its already-installed Python by absolute path; do not activate the Windows Anaconda path on Linux or silently install/upgrade packages.
- Starting estimation, mining, large decompression, deletion, environment changes, or long-running jobs requires authorization in the current task. A request to locate data authorizes inspection, not processing it.
- For authorized compute, inspect current load, memory, disk space and project instructions before choosing workers. The recorded 384 logical CPUs are not a worker quota. Avoid worker-by-BLAS oversubscription; use explicit numeric thread limits where appropriate. Do not stop other projects' jobs.
- Keep new outputs in the authorized project's new run directory, with logs and exact recovery paths. Protect raw data, frozen releases and old results. This access skill does not supersede project-specific data or research restrictions.

## Failure boundaries

- Timeout/no route: report the private-network access issue; check the existing LAN/VPN route if authorized. Do not create tunnels, expose ports or reconfigure networking on speculation.
- `Permission denied`: stop noninteractive retries and ask the user to restore existing SSH access. Do not embed passwords, copy keys into the skill, or install new authorized keys.
- Unknown/changed host key: stop and obtain trusted fingerprint verification. Do not use `StrictHostKeyChecking=no`, discard `known_hosts`, or blindly trust a newly scanned key.
- Unexpected hostname: stop; do not operate on a potentially different machine.

Report what was actually verified, with exact remote paths and observed limitations. Never store passwords, tokens, private keys or credential values in this skill or its logs.
