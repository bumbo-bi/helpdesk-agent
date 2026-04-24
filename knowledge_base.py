# A list of FAQ entries; in a real system this would be a database or a vector store
FAQS = [
    {
        "id": "billing-001",
        "topic": "billing",
        "question": "How do I update my credit card?",
        "answer": "Go to Settings > Billing > Payment Methods. Click 'Update Card', enter your new details, and click 'Save'. Changes will take effect on your next billing cycle."
    },
    {
        "id": "billing-002",
        "topic": "billing",
        "question": "When am I charged?",
        "answer": "HelpDesk charges on the 1st of each month for monthly plans, and annually on your signup anniversary date for annual plans. You'll receive an email notification 3 days prior to being charged."
    },
    {
        "id": "billing-003",
        "topic": "billing",
        "question": "What forms of payment do you accept?",
        "answer": "HelpDesk accepts credit/debit cards (Visa, Mastercard, AMEX, Discover) and PayPal."
    },
    {
        "id": "account-001",
        "topic": "account",
        "question": "How do I reset my password?",
        "answer": "On the login screen, click 'Forgot password'. A a reset link will be sent to your registered email within a few minutes."
    },
    {
        "id": "account-002",
        "topic": "account",
        "question": "How do I update my email?",
        "answer": "Go to Settings > Profile > Email. Click 'Update Email', enter your new details, and click 'Save'."
    },
    {
        "id": "account-003",
        "topic": "account",
        "question": "How do I delete my account?",
        "answer": "Go to Settings > Account > Delete Account. Note that this is permanent and cannot be reversed."
    },
    {
        "id": "integrations-001",
        "topic": "integrations",
        "question": "Does HelpDesk integrate with Slack?",
        "answer": "Yes. Install the HelpDesk Slack app from the Slack marketplace. Then, in HelpDesk, go to Settings > Integrations to authorize access."
    },
    {
        "id": "integrations-002",
        "topic": "integrations",
        "question": "Can I connect to Google Calendar?",
        "answer": "Yes, on Pro and Business plans. Go to Settings > Integrations > Google Calendar and authorize access."
    },
    {
        "id": "features-001",
        "topic": "features",
        "question": "How do I create a recurring task?",
        "answer": "When creating a task, click on 'Does not repeat', and toggle between daily, weekly, monthly, yearly, or custom intervals."
    },
    {
        "id": "features-002",
        "topic": "features",
        "question": "Can I export my data?",
        "answer": "Yes. Go to Settings > Data > Export. A CSV file containing all project and tasks will be sent to your registered email."
    },
]

def search_faqs(query: str) -> list:
    """
    Search FAQs by simple keyword matching.
    Returns a list of FAQ entries where the query terms appear in the question
    """
    query_words = query.lower().split()
    results = []
    for faq in FAQS:
        question_lower = faq["question"].lower()
        # If any query word appears in the question, consider it a match
        if any(word in question_lower for word in query_words):
            results.append(faq)
    return results
