import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    identity = os.environ.get("SEC_EDGAR_USER_AGENT", "")
    if "@" not in identity:
        raise RuntimeError("Set a real SEC_EDGAR_USER_AGENT locally")
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "sec_edgar_mcp.server"],
        env={**os.environ, "SEC_EDGAR_USER_AGENT": identity},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            print(json.dumps({"tool_count": len(listing.tools), "tools": [t.name for t in listing.tools]}))
            result = await session.call_tool("get_company_info", {"identifier": "0000320193"})
            if result.isError:
                raise RuntimeError(str(result.content))
            for content in result.content:
                if content.type == "text":
                    data = json.loads(content.text)
                    print(json.dumps(data, indent=2))
                    if not data.get("success") or data.get("company", {}).get("cik") != "0000320193":
                        raise AssertionError("Expected Apple company metadata")
            filings = await session.call_tool("get_recent_filings", {
                "identifier": "0000320193", "form_type": "10-K", "days": 730, "limit": 1,
            })
            if filings.isError:
                raise RuntimeError(str(filings.content))
            for content in filings.content:
                if content.type == "text":
                    data = json.loads(content.text)
                    rows = data.get("filings", [])
                    if not data.get("success") or not rows or rows[0].get("form_type") != "10-K":
                        raise AssertionError("No inspected 10-K filing returned")
                    row = rows[0]
                    accession = row["accession_number"]
                    row["source_url"] = ("https://www.sec.gov/Archives/edgar/data/320193/"
                                         + accession.replace("-", "") + "/" + accession + "-index.html")
                    print(json.dumps(row, indent=2))
            print("SEC MCP startup and live metadata/filing checks passed.")


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=90))
