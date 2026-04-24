import anthropic

# This creates a client that talks to Claude's servers
# It automatically reads the ANTHROPIC_API_KEY from the environment
client = anthropic.Anthropic()

# Prompt the user for their question
user_question = input("What do you want to ask Claude today? ")
response_style = input("How should Claude to respond? (e.g., 'like a pirate', 'at an elementary level'): ")

if response_style:
    system_prompt = f"Respond to all questions {response_style}."
else:
    system_prompt = "Respond helpfully and clearly."

# Send the question to Claude
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=system_prompt,
    messages=[
        {"role": "user", "content": user_question}
    ],
)

print(response.content[0].text)
