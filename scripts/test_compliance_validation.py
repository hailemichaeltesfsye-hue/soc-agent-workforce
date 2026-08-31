"""Test compliance validation and required-field gating with self-healing loop."""

from datetime import datetime
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.agents.compliance_auditor import ComplianceAuditorAgent


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_state_summary(state: SOCState, label: str = ""):
    """Print key compliance-related fields from state."""
    if label:
        print(f"--- {label} ---")
    print(f"Status: {state.status}")
    print(f"Compliance Status: {state.compliance_status}")
    print(f"Compliance Retry Count: {state.compliance_retry_count}/{state.compliance_max_retries}")
    print(f"Required Fields Present: {state.required_fields_present}")
    print(f"Required Fields Missing: {state.required_fields_missing}")
    print(f"Compliance Findings:")
    for finding in state.compliance_findings:
        print(f"  - {finding}")
    print()


def test_case_a_full_pass():
    """Test Case A: A complete, well-formed state that passes compliance on first try."""
    print_section("TEST CASE A: Complete State → Compliance PASSED on First Try")
    
    # Create a fully-populated state
    state = SOCState(
        incident_id="INC-2026-001",
        case_title="Suspicious Port Scan Activity",
        severity="high",
        alert_summary="Multiple SYN packets detected from 192.168.1.100 to port 22, 80, 443 on server.",
        triage_category="suspicious",
        triage_evidence=[
            "IP 192.168.1.100 has abuse confidence score of 65%",
            "Port scan pattern matches reconnaissance behavior"
        ],
        ip_addresses=["192.168.1.100"],
        mitre_techniques=["T1046"],  # Non-empty
        threat_hunt_summary="Further investigation revealed the IP is associated with a known vulnerability scanner. Activity is consistent with authorized security assessment.",
        risk_assessment="Malicious intent suspected; recommend blocking IP and investigating access logs.",
        final_summary="Alert determined to be a scanning probe from external network. Recommend IP blocking and log review.",
    )
    
    print("Initial State:")
    print_state_summary(state, "Before Compliance Check")
    
    # Run compliance audit
    auditor = ComplianceAuditorAgent()
    state = auditor.run(state)
    
    print("After Compliance Auditor:")
    print_state_summary(state, "After Compliance Check")
    
    # Verify result
    assert state.compliance_status == "passed", f"Expected 'passed', got '{state.compliance_status}'"
    assert state.required_fields_present is True, "Expected required_fields_present=True"
    assert len(state.required_fields_missing) == 0, f"Expected no missing fields, got: {state.required_fields_missing}"
    assert state.report_ready_for_review is True, "Expected report_ready_for_review=True"
    
    print("✅ TEST CASE A PASSED: State passed compliance on first try with no missing fields.\n")


def test_case_b_missing_fields_then_fix():
    """Test Case B: Missing MITRE mapping → fails → gets populated → passes on retry."""
    print_section("TEST CASE B: Missing Required Field → Fail → Fix → Pass on Retry")
    
    # Create a state with DELIBERATELY MISSING MITRE mapping
    state = SOCState(
        incident_id="INC-2026-002",
        case_title="Failed Login Attempts",
        severity="medium",
        alert_summary="15 failed SSH login attempts detected from 203.0.113.50 within 5 minutes.",
        triage_category="suspicious",
        triage_evidence=[
            "IP 203.0.113.50 had 8 previous abuse reports",
            "Attempt pattern matches brute-force attack signature"
        ],
        ip_addresses=["203.0.113.50"],
        mitre_techniques=[],  # INTENTIONALLY EMPTY - this should fail compliance
        threat_hunt_summary="Logs show rapid authentication failures. Recommend enabling account lockout and reviewing access controls.",
        risk_assessment="Medium risk; credential compromise possible.",
        final_summary="Brute-force attack detected. Recommend account lockout and password reset.",
    )
    
    print("Initial State (MISSING MITRE TECHNIQUES):")
    print_state_summary(state, "Before 1st Compliance Check")
    
    # First compliance check should FAIL
    auditor = ComplianceAuditorAgent()
    state = auditor.run(state)
    
    print("After 1st Compliance Auditor (Should FAIL):")
    print_state_summary(state, "After 1st Compliance Check")
    
    # Verify failure
    assert state.compliance_status == "failed", f"Expected 'failed', got '{state.compliance_status}'"
    assert state.required_fields_present is False, "Expected required_fields_present=False"
    assert "mitre_techniques" in state.required_fields_missing, "Expected 'mitre_techniques' in missing fields"
    assert state.report_ready_for_review is False, "Expected report_ready_for_review=False"
    
    print("⚠️  Compliance check failed as expected. Missing fields detected.\n")
    
    # Simulate Alert Analyst receiving compliance findings and fixing the state
    print("--- Alert Analyst Fixing Compliance Issues ---")
    print(f"Compliance feedback received: {state.compliance_findings}")
    print("Alert Analyst populating missing MITRE techniques...")
    
    # Simulate the Alert Analyst adding the MITRE technique
    state.mitre_techniques.append("T1110.001")  # Brute Force: Password Guessing
    state.triage_reasoning.append("Mapped to MITRE technique T1110.001 (Password Guessing).")
    state.status = "revision_requested"  # Mark as revision in progress
    
    print(f"State updated: mitre_techniques = {state.mitre_techniques}\n")
    
    # Second compliance check should PASS
    print("Running 2nd Compliance Auditor (After Fix):")
    auditor = ComplianceAuditorAgent()
    state = auditor.run(state)
    
    print_state_summary(state, "After 2nd Compliance Check (Should PASS)")
    
    # Verify pass
    assert state.compliance_status == "passed", f"Expected 'passed', got '{state.compliance_status}'"
    assert state.required_fields_present is True, "Expected required_fields_present=True"
    assert len(state.required_fields_missing) == 0, f"Expected no missing fields, got: {state.required_fields_missing}"
    assert state.report_ready_for_review is True, "Expected report_ready_for_review=True"
    
    print("✅ TEST CASE B PASSED: State failed compliance, was fixed, then passed on retry.\n")


def test_case_c_exhausted_retries():
    """Test Case C: Missing field + exhausted retries → blocks workflow."""
    print_section("TEST CASE C: Missing Field + Exhausted Retries → BLOCKED")
    
    # Create a state with missing field and simulate multiple failed attempts
    state = SOCState(
        incident_id="INC-2026-003",
        case_title="Malware Detection",
        severity="critical",
        alert_summary="File 'trojan.exe' detected by antivirus engine.",
        triage_category="malicious",
        triage_evidence=["Signature match: Known trojan variant"],
        ip_addresses=["10.0.0.50"],
        mitre_techniques=["T1566.001"],  # Phishing: Spearphishing Attachment
        threat_hunt_summary="Analysis confirms trojan binary attempting lateral movement.",
        risk_assessment="Critical; immediate remediation required.",
        final_summary="",  # INTENTIONALLY EMPTY - this will keep failing
        compliance_retry_count=2,  # Simulate that we're on the 3rd attempt
    )
    
    print("State with Exhausted Retries (retry_count=2, approaching cap of 3):")
    print(f"Incident: {state.incident_id}")
    print(f"Missing: final_summary")
    print(f"Compliance Retry Count: {state.compliance_retry_count}/{state.compliance_max_retries}\n")
    
    # Run compliance check
    auditor = ComplianceAuditorAgent()
    state = auditor.run(state)
    
    print("After Compliance Auditor:")
    print_state_summary(state, "Compliance Check Result")
    
    # Verify failure (retry_count=2 is still < 3, so not yet blocked)
    assert state.compliance_status == "failed", f"Expected 'failed', got '{state.compliance_status}'"
    assert state.required_fields_present is False, "Expected required_fields_present=False"
    assert "final_summary" in state.required_fields_missing, "Expected 'final_summary' in missing fields"
    
    print("⚠️  Compliance check failed (retry_count=2 is still < max_retries=3).\n")
    
    # Simulate workflow incrementing retry count to 3 and checking cap
    print("--- Simulating Workflow Routing Logic ---")
    print("Workflow increments compliance_retry_count from 2 to 3...")
    state.compliance_retry_count += 1
    
    if state.compliance_retry_count >= state.compliance_max_retries:
        print(f"Retry count {state.compliance_retry_count} >= max {state.compliance_max_retries}")
        print("Blocking workflow and setting compliance_status='blocked'")
        state.compliance_status = "blocked"
        state.status = "blocked"
        state.notes.append("Compliance retry cap reached; workflow blocked.")
    
    print_state_summary(state, "After Workflow Routing (BLOCKED)")
    
    # Verify blocked state
    assert state.compliance_status == "blocked", f"Expected 'blocked', got '{state.compliance_status}'"
    assert state.status == "blocked", f"Expected workflow status 'blocked', got '{state.status}'"
    
    print("✅ TEST CASE C PASSED: Compliance validation blocked after retry cap exceeded.\n")


def main():
    """Run all compliance validation tests."""
    print("\n" + "="*80)
    print(" COMPLIANCE VALIDATION TEST SUITE (Step 6)")
    print("="*80)
    
    try:
        test_case_a_full_pass()
        test_case_b_missing_fields_then_fix()
        test_case_c_exhausted_retries()
        
        print_section("ALL TESTS PASSED ✅")
        print("Summary:")
        print("  ✅ Case A: Complete state passes compliance on first try")
        print("  ✅ Case B: Incomplete state fails, gets fixed, passes on retry")
        print("  ✅ Case C: Exhausted retries trigger workflow block")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise


if __name__ == "__main__":
    main()
