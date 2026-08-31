# SOC Agent Workforce Architecture

```mermaid
flowchart TD
    U[User / Streamlit UI] --> M[SOC Manager\nintake_and_route]
    M --> A[Alert Analyst\ntriage_alert]
    A --> H[Threat Hunter\nreview_triage]

    H -->|triage is strong and complete| C[Compliance Auditor\nvalidate_report_fields]
    H -->|triage weak / incomplete| R[Threat Hunter\nrequest_revision]
    R --> AA[Alert Analyst\nrevise_triage]
    AA -->|retry_count < 3| H
    AA -->|retry_count >= 3| C

    C -->|required fields present| I[Incident Reporter\ndraft_incident_report]
    C -->|missing required fields| B[SOC Manager\nblock_and_request_fix]
    B --> A

    I --> HP[Human Approval\nHITL checkpoint]
    HP -->|approved| E[SOC Manager\nescalate_or_close_case]
    HP -->|rejected / revise| M

    E --> F[Final State\nEscalated or Closed]

    classDef manager fill:#e3f2fd,stroke:#1565c0,color:#000;
    classDef analyst fill:#e8f5e9,stroke:#2e7d32,color:#000;
    classDef hunter fill:#fff3e0,stroke:#ef6c00,color:#000;
    classDef auditor fill:#f3e5f5,stroke:#7b1fa2,color:#000;
    classDef reporter fill:#fce4ec,stroke:#c2185b,color:#000;
    classDef human fill:#f1f8e9,stroke:#558b2f,color:#000;
    classDef final fill:#eceff1,stroke:#455a64,color:#000;

    class M manager;
    class A,AA analyst;
    class H,R hunter;
    class C,B auditor;
    class I reporter;
    class HP human;
    class E,F final;
```

This workflow follows the supervisor pattern: the SOC Manager routes the investigation, the Alert Analyst performs initial triage, the Threat Hunter critiques and repairs weak analysis, the Compliance Auditor validates required fields, the Incident Reporter drafts the final report, and a human reviewer approves escalation or closure before the case is finalized.
