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
