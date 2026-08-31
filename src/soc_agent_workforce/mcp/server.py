from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .abuseipdb_client import check_ip_reputation as check_ip_reputation_api
from .mitre_dataset import lookup_mitre_technique as lookup_mitre_technique_api

mcp = FastMCP("soc-agent-workforce")


@mcp.tool()
def check_ip_reputation(
    ip_address: str,
    categories: list[int] | None = None,
    max_age_in_days: int | None = None,
    verbose: bool | None = None,
) -> dict[str, Any]:
    """Return AbuseIPDB reputation metadata for a suspicious IP address."""
    return check_ip_reputation_api(
        ip_address=ip_address,
        categories=categories,
        max_age_in_days=max_age_in_days,
        verbose=verbose,
    )


@mcp.tool()
def lookup_mitre_technique(
    technique_id: str | None = None,
    technique_name: str | None = None,
    tactic: str | None = None,
    keyword: str | None = None,
) -> dict[str, Any]:
    """Lookup the local MITRE ATT&CK dataset by technique ID, name, tactic, or keyword."""
    return lookup_mitre_technique_api(
        technique_id=technique_id,
        technique_name=technique_name,
        tactic=tactic,
        keyword=keyword,
    )


if __name__ == "__main__":
    mcp.run()
