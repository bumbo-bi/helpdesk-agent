import anthropic
from knowledge_base import search_faqs, FAQS
client = anthropic.Anthropic()

# Verify this is a current GA model
MODEL = "claude-opus-4-8"

# Define the tools Claude can use
# Each tool as a name, description, and input schema (what arguments it takes)
TOOLS = [
    {
        "name": "search_faqs",
        "description": (
            "Search the HelpDesk FAQ knowledge base for answers to customer questions. "
            "Use this tool to find relevant FAQ entries based on the user's question. "
            "Returns a list of matching FAQ entries with their questions and answers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms related to the customer's question"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Escalate the conversation to a human support agent. Use this when: "
            "(1) the FAQ search returns no useful results, "
            "(2) the question involves account-specific information you can't access, "
            "(3) the user explicitly asks for a human, or "
            "(4) the issue is complex or emotionally charged. "
            "Provide a clear handoff summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why is this being escalated"
                },
                "summary": {
                    "type": "string",
                    "description": "Summary of what the user asked and what's been tried so far"
                }
            },
            "required": ["reason", "summary"]
        }
    },
    {
        "name": "request_clarification",
        "description": (
            "Ask the user for more information when their question is too vague "
            "or could mean multiple things. **ALWAYS use this tool to ask clarifying questions** "
            " - never ask clarifying questions in free-text responses. "
            "This tool is the only correct mechanism for requesting clarification."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The clarifying question to ask the user"
                }
            },
            "required": ["question"]
        }
    }
]
SYSTEM_PROMPT = """You are a support agent for HelpDesk, a SaaS.

Resolve each customer message by taking exactly ONE structured action. Follow this
decision procedure on every turn:

1. ALWAYS call search_faqs first. Never answer from general knowledge about SaaS products.
2. If search_faqs returns an entry that clearly answers the question, reply with that
   answer in a friendly, concise way. This is the ONLY situation in which you may end
   your turn with a plain-text message.
3. If the question is out of scope - the FAQ has nothing relevant, it needs
   account-specific data you cannot see, the user asks for a human, or the issue is
   complex or emotionally charged - call escalate_to_human. Do not guess.
4. If the question is genuinely ambiguous or too vague to search or answer (for example
   "it's not working", "I have a question about my account", or a bare greeting like
   "hi"), call request_clarification.

Hard rules:
- NEVER end your turn by asking the user a question in plain text. If you need more
  information, you MUST call request_clarification. A plain-text message that asks the
  user for more details is a bug, not a valid answer.
- NEVER invent answers, plan names, prices, or features that are not in the FAQ. When
  in doubt, escalate.
- Keep responses short and direct. Customers want answers, not essays.
"""

def run_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if tool_name == "search_faqs":
        results = search_faqs(tool_input["query"])
        if not results:
            return "No matching FAQs found."
        # Format results as a string Claude can read
        formatted = "\n\n".join(
            f"ID: {r['id']}\nQ: {r['question']}\nA: {r['answer']}"
            for r in results
        )
        return formatted
    elif tool_name == "escalate_to_human":
        return (
            f"ESCALATED. Reason: {tool_input['reason']}. "
            f"Summary handed off: {tool_input['summary']}"
        )
    elif tool_name == "request_clarification":
        return f"CLARIFICATION REQUESTED: {tool_input['question']}"
    else:
        return f"Unknown tool: {tool_name}"
    
def handle_user_message(user_message: str, verbose: bool = True) -> dict:
    """
    Send a user message to the agent and run the full loop until a final response is received.
    Returns a dict with the final text response and medatada about what happened.
    """
    # Handle empty input before calling the API
    if not user_message or not user_message.strip():
        return {
            "response": "I didn't catch that - could you let me know what you would like help with?",
            "tool_calls": [],
            "escalated": False,
            "clarification_requested": True, # treat empty input as needing clarification
        }
    messages = [{"role": "user", "content": user_message}]
    tool_calls_made = []
    # The agent loop: keep calling Claude until it stops using tools
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        if verbose:
            print(f"\n--- Turn (stop_reason: {response.stop_reason})---")
        # If Claude doesn't use a tool, we have reached the final response
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return {
                "response": final_text,
                "tool_calls": tool_calls_made,
                "escalated": any(t["name"] == "escalate_to_human" for t in tool_calls_made),
                "clarification_requested": any(t["name"] == "request_clarification" for t in tool_calls_made),
            }
        # If Claude wants to use tools, execute them and return results
        elif response.stop_reason == "tool_use":
            # Append Claude's response with tool calls
            messages.append({"role": "assistant", "content": response.content})
            # Run each tool Claude called
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"Tool called: {block.name}")
                        print(f"Input: {block.input}")
                    result = run_tool(block.name, block.input)
                    if verbose:
                        print(f"Result: {result[:150]}...")
                    tool_calls_made.append({"name": block.name, "input": block.input})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            # Add the tool results so Claude can use
            messages.append({"role": "user", "content": tool_results})
            continue
        # Unexpected stop reason - bail out
        else:
            return {
                "response": f"Unexpected stop reason: {response.stop_reason}",
                "tool_calls": tool_calls_made,
                "escalated": False,
                "clarification_requested": False,
            }
            
# Manual test
if __name__ == "__main__":
    test_queries = [
        "How do I change my credit card?",
    #    "I want to update my password",
    #    "Does this work with Slack?",
    #    "My account is broken",
    ]
    for q in test_queries:
        print(f"\n{'='*60}\nUSER: {q}")
        result = handle_user_message(q, verbose=True)
        print(f"\nFINAL RESPONSE: {result['response']}")
        print(f"Escalated: {result['escalated']}")