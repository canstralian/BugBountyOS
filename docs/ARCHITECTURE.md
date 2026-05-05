# BugBountyOS Architecture: The Timescape Model

## Conceptual Model
 BugBountyOS is structured as a biological entity where each standalone repository is a specialized **Vector** assigned a specific role in the system.

### The Constitutional Layer
*   **Nervous System (Events/Bus):** Orchestrates communication between vectors.
*   **Immune System (Guardrails/Policies):** Enforces security and ethical bounds.
*   **Cognition (LLM/NLP):** High-level decision making and report synthesis.

## Directory Structure
```text
bugbountyos/
├── vectors/
│── dashboard/      #Role: Visual Cortex (from BugBountyBot)
│── pipeline/       #Role: Metabolism (from BugBountyPipeline)
│── storage/        #Role: Memory (from BugBountyManager)
├── contracts/          #Vector role definitions and exit criteria
├── docs/               #Architecture and Timescape specs
```J
## Migration Strategy
Vectors are imported using `git subtree add --squash`. This preserves the historical context of each project as a single, immutable graft into the OS graph.