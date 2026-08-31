from __future__ import annotations

import os
from unittest.mock import patch

from soc_agent_workforce.mcp.abuseipdb_client import check_ip_reputation
from soc_agent_workforce.mcp.mitre_dataset import lookup_mitre_technique


def main() -> None:
    print("=== AbuseIPDB direct tool check ===")
    if not os.getenv("ABUSEIPDB_API_KEY"):
        mock_payload = {
            "data": {
                "ipAddress": "8.8.8.8",
                "isPublic": True,
                "abuseConfidenceScore": 82,
                "totalReports": 44,
                "categories": [18, 21],
                "countryCode": "US",
                "countryName": "United States",
                "isp": "Google LLC",
                "domain": "google.com",
            }
        }
        with patch("soc_agent_workforce.mcp.abuseipdb_client.httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_payload
            result = check_ip_reputation("8.8.8.8")
            print(result)
    else:
        print(check_ip_reputation("8.8.8.8"))

    print("\n=== MITRE local dataset lookup ===")
    print(lookup_mitre_technique(technique_id="T1003.001"))
    print(lookup_mitre_technique(keyword="PowerShell"))


if __name__ == "__main__":
    main()
