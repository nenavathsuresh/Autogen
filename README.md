## MCP Audit Report Tool Architecture
This documentation provides a high-level explanation of an audit report creation and retrieval tool. It is built with the Model Context Protocol (MCP), using YAML‑driven orchestration, an Insite REST tool, and a backend Audit API.

## Architecture Overview
Purpose:
To create and fetch audit reports through a modular, layered system where the Agent, MCP, Insite tool, and REST API interact via clearly separated responsibilities.

### System Architecture Diagram
graph TD
    A[Agent (YAML instruction input)]
    B[MCP Client / Server]
    C[Insite Tool]
    D[Audit REST API]
    E[Audit Database]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> D
    D --> C
    C --> B
    B --> A


### Data Flow Architecture
```mermaid
flowchart TD
    YAML[“YAML instruction”] --> Agent[Agent]
    Agent --> MCP[MCP orchestration]
    MCP --> Tool[Insite Tool]
    Tool --> API[Audit REST API]
    API --> DB[(Database)]
    DB --> API
    API --> Tool
    Tool --> MCP
    MCP --> Agent
    Agent --> User[User receives output]


### Component Architecture
classDiagram
    class Agent {
        +parseYAML()
        +initiateOperation()
    }
    class MCP {
        +parseInstruction()
        +routeToTool()
    }
    class Insite {
        +createReport()
        +fetchReport()
        +makeRESTCall()
    }
    class AuditAPI {
        +POST /auditReports
        +GET /auditReports/{id}
    }
    class Database {
        +storeReport()
        +retrieveReport()
    }

    Agent -- MCP
    MCP -- Insite
    Insite -- AuditAPI
    AuditAPI -- Database
```

## ⚡ Sequence Diagram: Create and Fetch Audit Report
mermaid

sequenceDiagram
    participant Agent
    participant MCP
    participant Insite
    participant API

    Agent->>MCP: “createAuditReport” (with YAML params)
    MCP->>Insite: invoke create action
    Insite->>API: POST /auditReports
    API-->>Insite: { reportId, metadata }
    Insite-->>MCP: result
    MCP-->>Agent: { reportId }

    Agent->>MCP: “fetchAuditReport(reportId)”
    MCP->>Insite: invoke fetch action
    Insite->>API: GET /auditReports/{id}
    API-->>Insite: full report payload
    Insite-->>MCP: report content
    MCP-->>Agent: full report

#### 2. Sequence Diagram (Textual)

```
Agent        MCP         Insite Tool      REST API
 |            |               |               |
 |-----YAML-->|               |               |
 |            |----Parse----->|               |
 |            |               |---POST/GET--->|
 |            |               |<---Response---|
 |<----------Response---------|               |
```

## 📚 Architecture Context: MCP Overview
The Model Context Protocol (MCP) is a standardized, JSON-RPC 2.0–based protocol that connects AI agents to external tools and data sources in a consistent way 

MCP provides three core primitives: Tools (callable functions), Resources (structured data), and Prompts (templated instructions) 

AI clients discover available tools from MCP servers, invoke them dynamically, and receive structured responses—all routed via the MCP infrastructure 

## 🔧 Technology Stack
Layer	Technology / Role
Agent	Application layer parsing YAML and triggering MCP calls
MCP	Standard protocol (JSON-RPC 2.0) routing and orchestration
Insite Tool	Custom component (Python/Node.js) acting as MCP tool with REST logic
REST API	Backend service implementing POST /auditReports & GET /auditReports/{id}
Database	Persistent storage for audit report metadata and content
Communication	HTTP/HTTPS, JSON-based messaging, schema validation via JSON Schema

### Technology Stack

- **MCP Platform:** Orchestrates actions and parses YAML instructions.
- **YAML:** Human-readable configuration for defining audit tasks.
- **Insite Tool:** Python/Node.js module acting as a REST client.
- **REST API:** Backend services (typically over HTTP/HTTPS, exchanging JSON).
- **Protocols:** HTTP(S) for secure communication; JSON as the data format.

## ✅ Summary
This architecture decouples command orchestration (Agent → MCP) from operational execution (Insite → REST API), supporting maintainability, scalability, traceability, and secure integration. Each part is responsible for a clear function, enabling flexible extension or replacement if needed.

You can paste these Mermaid diagram definitions into your .md file (e.g. audit_report_architecture.md) and render them live in GitHub, GitLab, or Mermaid Live Editor. Let me know if you'd like deployment diagrams, swimlane charts, or integration with MCP gateways!

