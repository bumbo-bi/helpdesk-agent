# HelpDesk Support Agent
An LLM-powered customer support agent for a fictional SaaS company (HelpDesk), built to explore agent design patterns (e.g., tool use, escalation logic, and measurable quality).

## Why I built this
I previously shipped a rules-based automated response system that triaged inbound requests and answered FAQs based on keyword matching, using Microsoft Power Automate. It worked, but there were limitations (e.g., paraphrased questions, compound intents, and anything requiring judgment). This project revisits the same problem with an LLM agent to learn firsthand how it compares to the rules-based approach and where new challenges appear.
## What it does
This agent handles customer support questions for HelpDesk. It can:
- Search a structured FAQ knowledge base (via tool use)
- Escalate to a human when the FAQ doesn't provide the answer
- Ask for clarification when the user's question is genuinely ambiguous
- Decline to answer questions it has no data for
## How it works
- Built on Claude (Anthropic API) with tool use
- Tools: `search_faqs`, `escalate_to_human`, `request_clarification`
- System prompt that enforces: search before answering, escalate rather than hallucinate
## Evaluation
20 test cases covering happy path (exact FAQ matches), paraphrased (same intent but different words), multi-part (compound questions), ambiguous (could mean several things), out-of-scope (not handled by FAQ), trick (agent must not hallucinate), and edge case (greetings, empty input) queries. Each test asserts an expected outcome (answered / clarified / escalated).
| Category | Pass rate |
|----------|-----------|
| happy path | 4/4 |
| paraphrased | 4/4 |
| multi_part | 2/2 |
| ambiguous | 2/2 |
| out_of_scope | 4/4 |
| trick | 2/2 |
| edge_case | 2/2 |
| **Overall** | **20/20** |
## What I learned
Initial evaluation showed three failures (one in ambiguous and two in edge cases). In addition, the edge cases produced inconsistent results. Investigation revealed two distinct issues:
1. The agent was asking clarifying questions in free text instead of calling `request_clarification`, bypassing the structured clarification path. Fixed by strengthening the system prompt to require the tool, which reduced the failure rate; the ambiguous and edge cases have passed on repeated runs since.
2. Empty user input crashed the API call before reaching the agent. Fixed by adding an upstream guard that returns a clarification response without calling the API.

Because of the inconsistent results in prior edge case runs, the fix for #1 is a mitigation. The failure is probabilistic: a prompt lowers how often the model takes the free-text path without changing what the code does when it still does.