<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# I said replace content with insites documentaion:

Absolutely! Here’s a clean README.md documentation template for your **Insite Audit Report Tool**, using the Model Context Protocol (MCP). This fully replaces all the prior SDR/Sales documentation with your high-level architecture, workflow, and diagrams focused on Insite + MCP + Audit reports.

```markdown
# Insite Audit Report Tool — MCP Architecture

This documentation explains the modular, context-driven audit report tool built using the Model Context Protocol (MCP), orchestrating requests via YAML, Insite REST tool, and a backend Audit API.

---

## 📜 Overview

The Insite Audit Report tool automates the creation and fetching of audit reports through:

- YAML-driven agent orchestration
- Model Context Protocol (MCP) for tool invocation
- Insite tool as a secure REST API client
- Backend Audit API and persistent data store

---

## 📃 Table of Contents

- [👷 Architecture Overview](#-architecture-overview)
  - [System Architecture Diagram](#system-architecture-diagram)
  - [Data Flow Architecture](#data-flow-architecture)
  - [Component Architecture](#component-architecture)
  - [Workflow Diagrams](#workflow-diagrams)
  - [Technology Stack](#technology-stack)
- [🛠️ Usage Summary](#️-usage-summary)

---

## 👷 Architecture Overview

The architecture is modular, with each component focusing on a distinct responsibility for maintainability, traceability, and extensibility.

### System Architecture Diagram

```

graph TD
A[Agent (YAML instruction input)] --> B[MCP Client / Server]
B --> C[Insite Tool]
C --> D[Audit REST API]
D --> E[Audit Database]
E --> D
D --> C
C --> B
B --> A

```

---

### Data Flow Architecture

```

flowchart TD
YAML["YAML instruction"] --> Agent[Agent]
Agent --> MCP[MCP orchestration]
MCP --> Tool[Insite Tool]
Tool --> API[Audit REST API]
API --> DB[(Database)]
DB --> API
API --> Tool
Tool --> MCP
MCP --> Agent
Agent --> User[User receives output]

```

---

### Component Architecture

```

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
+POST_auditReports()
+GET_auditReports_by_id()
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

---

### Workflow Diagrams

#### Sequence Diagram — Create/Fetch Audit Report

```

sequenceDiagram
participant Agent
participant MCP
participant Insite
participant API

Agent->>MCP: "createAuditReport" (with YAML params)
MCP->>Insite: invoke create action
Insite->>API: POST /auditReports
API-->>Insite: { reportId, metadata }
Insite-->>MCP: result
MCP-->>Agent: { reportId }

Agent->>MCP: "fetchAuditReport(reportId)"
MCP->>Insite: invoke fetch action
Insite->>API: GET /auditReports/{id}
API-->>Insite: full report payload
Insite-->>MCP: report content
MCP-->>Agent: full report

```

---

## 🔧 Technology Stack

| Layer         | Technology / Description                                      |
|---------------|--------------------------------------------------------------|
| **Agent**     | Reads YAML, triggers MCP actions                             |
| **MCP**       | JSON-RPC 2.0 context protocol orchestration                  |
| **Insite**    | REST API client (Python/Node.js microservice)                |
| **REST API**  | Backend service for audit reports                            |
| **Database**  | Persistent storage (e.g., PostgreSQL, MongoDB)               |
| **Protocols** | HTTP(REST), YAML (for instruction), JSON-RPC (for MCP)       |

---

## 🛠️ Usage Summary

**Workflow:**
- Agent parses YAML to generate audit requests
- MCP routes and orchestrates the request, coordinating structured tool invocations
- Insite tool securely calls the REST backend
- Results are returned to the agent and ultimately to the end user or system

_This modular architecture supports scaling, secure integration, policy enforcement, and clear separation of concerns. Standard YAML and MCP protocol make it easy to extend or replace components as business needs evolve._

---

> Paste these Mermaid diagrams as shown for live rendering on GitHub, GitLab, or Mermaid Live Editor. If you need additional detail (deployment, integration, swimlanes), just ask!
```

**How to use:**

- Replace your README.md content with this block.
- The diagrams will render anywhere Markdown+Mermaid is supported (GitHub .md, GitLab, VSCode with plugins, or Mermaid Live Editor).

Let me know if you want even more detailed flows, specific sequence expansion, or embedded quickstart code samples for your Insite tool!

