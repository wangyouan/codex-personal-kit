# Verified AMD server locations

Observed on 2026-10-13 at `user@172.16.10.68`, hostname `wyaamd-server001`. These are discovery starting points, not guarantees about current releases, complete coverage or data semantics.

## Storage and database roots

Mounted data directories: `/data/disk1`, `/data/disk2`, `/data/disk3`, `/data/disk4`, `/data/disk5`. Do not assume their free space or purpose from the names; check before writing.

| Data | Verified location |
|---|---|
| WRDS collection on disk1 | `/data/disk1/database/wrds/` |
| BvD family | `/data/disk1/database/wrds/bvd/` |
| BvD Orbis archive directory | `/data/disk1/database/wrds/bvd/bvdorbis/` |
| Separate Orbis export | `/data/disk5/data/bvd/1900_2020_bvd_orbis_state_lm.zip` |
| CNRDS | `/data/disk4/database/CNRDS/` |
| CSMAR | `/data/disk4/database/CSMAR/` |
| Revelio Labs | `/data/disk4/database/Revelio Labs/` |
| Another WRDS directory | `/data/disk4/database/wrds/` |

The two WRDS roots are distinct observed locations. Do not assume they are equivalent copies or that disk4 contains all WRDS/BvD data.

### BvD Orbis archives

| File under the Orbis archive directory | Observed bytes | Approximate decimal GB |
|---|---:|---:|
| `ob_l.zip` | 21,789,871,010 | 21.8 |
| `ob_m.zip` | 75,388,448,246 | 75.4 |
| `ob_s.zip` | 463,652,908,521 | 463.7 |

The BvD parent also contains `ama_l.zip`, `ama_m.zip`, `ama_s.zip`, `ama_v.zip`, `bankf.zip`, `is.zip`, `retired.zip`, and an `os/` directory with SAS files. Do not confuse these with the specific `bvdorbis/` archive directory.

The separate disk5 ZIP was 247,542,345 bytes. Its ZIP directory contains one member, `vkevjhvg7gdl9kad.csv`, with uncompressed size 3,459,370,199 bytes. The name `1900_2020_bvd_orbis_state_lm.zip` does not establish actual time coverage, variables, completeness, or relationship to the disk1 archives.

Use ZIP central-directory metadata (`zipfile.ZipFile(...).infolist()`) to inspect members and uncompressed sizes without extracting full datasets. Print only relevant names or a bounded preview. Inspect schema/small row samples only if needed for the current task; do not print bulk proprietary records or extract hundreds of GB merely to locate data. Hashing enormous archives is unnecessary for a directory-location question.

## BoardGenderDiversity project

| Purpose | Location |
|---|---|
| Physical project root | `/data/disk5/projects/BoardGenderDiversity/` |
| Convenience entry, verified to resolve to that root | `/home/user/projects/BoardGenderDiversity/` |
| Existing dedicated Python | `/home/user/bgd_rsi_runtime/envs/bgd_rsi_py312/bin/python` |
| Standard-library inspection Python | `/usr/bin/python3` (resolved to `/usr/bin/python3.12`) |
| Local Windows project | `D:/Users/Projects/BoardGenderDiversity/` |
| Document delivery directory | `D:/OneDrive/Projects/BoardGenderDiversity/writing/` |

Use absolute runtime and physical project paths for remote jobs. For authorized BGD numerical work the tested command prefix is:

```text
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 ARROW_NUM_THREADS=1 /home/user/bgd_rsi_runtime/envs/bgd_rsi_py312/bin/python
```

Do not infer package versions solely from the environment name. Do not conflate local Windows Anaconda with the Linux research environment. Use another project's configured runtime when working on another project.

BGD convention: main work directories contain process/intermediate/temp files; OneDrive holds delivery documents; Joplin holds project notes; Zotero manages literature collections. A server-access request does not authorize changing any of those systems.

Read the relevant project instructions, release manifests and handoff before analysis. As a dated navigation aid, the completed 66 task used run `bgd_rsi_complete_measures_20261012_01` with:

- Report: `reports/bgd_rsi/67_bgd_rsi_all_measurements_and_ownership_results.md`.
- Handoff and exact artifact paths: `outputs/bgd_rsi/complete_measures/bgd_rsi_complete_measures_20261012_01/handoff/artifact_index.json` and sibling `handoff.md` / `final_acceptance.json`.
- New extension: `data/processed/bgd_rsi/extensions/bgd_rsi_complete_measures_20261012_01/`.

These paths are relative to the physical server project root. That task stopped after delivery; recording its paths does not authorize a new mining round or identify it as the latest release forever.
