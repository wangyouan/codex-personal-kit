# Local SEC EDGAR setup

This is a maintained adaptation of John Barrios's MIT-licensed workflow:
`Barrios88/barrios-skills`, commit `d50afc62f4c67535a1949d029dfa0462feb906fd`,
path `skills/research-tools/sec-edgar`. The upstream notice is retained in LICENSE.
Unsupported frontmatter and collection-relative links were replaced. The current
MCP is built on sec-edgar-toolkit, not edgartools.

The separate [sec-edgar-mcp](https://github.com/stefanoamorelli/sec-edgar-mcp)
software is AGPL-3.0. It is installed locally, not redistributed in this kit.

## Windows installation

Create a dedicated Python 3.11+ environment under
`~/.codex/runtimes/sec-edgar-py`, using a working full Python interpreter:

```powershell
python -m venv (Join-Path $env:USERPROFILE '.codex\runtimes\sec-edgar-py')
$python = Join-Path $env:USERPROFILE '.codex\runtimes\sec-edgar-py\Scripts\python.exe'
& $python -m pip install 'sec-edgar-mcp==1.1.0'
& $python -m pip check
```

Register a stdio server named `sec-edgar` in local Codex configuration, using the
environment's Python executable, arguments `-m sec_edgar_mcp.server`, and env
`SEC_EDGAR_USER_AGENT` set to the user's real `Name (email)`.
Resolve the local executable path; do not copy another computer's config.
Never expose the unauthenticated HTTP transport to the network.

Run `scripts/smoke_test.py` with that Python and User-Agent to initialize MCP,
list tools, and inspect a public company's submission metadata. Restart Codex
after registration if its current tool list does not include the new server.

Primary access requirements: [SEC developer resources](https://www.sec.gov/about/developer-resources).
