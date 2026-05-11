from agent import handle_user_message

TEST_CASES = [
    # Happy path (exact FAQ matches)
    {"input": "How do I update my credit card?", "expected_outcome": "answered", "category": "happy path"},
    {"input": "How do I reset my password?", "expected_outcome": "answered", "category": "happy path"},
    {"input": "Does HelpDesk integrate with Slack?", "expected_outcome": "answered", "category": "happy path"},
    {"input": "How do I create a recurring task?", "expected_outcome": "answered", "category": "happy path"},
    # Paraphrased (same intent but different words - where keyword matching fails)
    {"input": "How can I pay?", "expected_outcome": "answered", "category": "paraphrased"},
    {"input": "I want to close my account", "expected_outcome": "answered", "category": " paraphrased"},
    {"input": "Will this sync with my Google Calendar?", "expected_outcome": "answered", "category": "paraphrased"},
    {"input": "Is it possible to download my data?", "expected_outcome": "answered", "category": "paraphrased"},
    # Multi-part questions
    {"input": "How do I pay and when will I be charged?", "expected_outcome": "answered", "category": "multi_part"},
    {"input": "Is it possible to change my email and password?", "expected_outcome": "answered", "category": "multi_part"},
    # Ambiguous (request clarification OR make reasonable guess)
    {"input": "It is not working", "expected_outcome": "clarified", "category": "ambiguous"},
    {"input": "I have a question about my account", "expected_outcome": "clarified", "category": "ambiguous"},
    # Out of scope (escalate)
    {"input": "I want to speak to a human", "expected_outcome": "escalated", "category": "explicit_request"},
    {"input": "Why was I charged $1234 last Friday?", "expected_outcome": "escalated", "category": "account_specific"},
    {"input": "All my data is gone and I am furious", "expected_outcome": "escalated", "category": "emotional"},
    {"input": "Does HelpDesk integrate with Microsoft Teams?", "expected_outcome": "escalated", "category": "out_of_scope"},
    # Trick questions (should not hallucinate)
    {"input": "What plan levels do you offer?", "expected_outcome": "escalated", "category": "no_faq_coverage"},
    {"input": "Can I white-label HelpDesk?", "expected_outcome": "escalated", "category": "no_faq_coverage"},
    # Edge cases
    {"input": "hi", "expected_outcome": "clarified", "category": "greeting"},
    {"input": "", "expected_outcome": "clarified", "category": "empty"},
]

def classify_outcome(result: dict) -> str:
    """Determine what actually happened from the agent's response."""
    if result["escalated"]:
        return "escalated"
    elif result["clarification_requested"]:
        return "clarified"
    else:
        return "answered"
    
def run_evaluation():
    results = []
    for i, case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Testing: {case['input'][:60]}...")
        try:
            agent_result = handle_user_message(case["input"], verbose=False)
            actual = classify_outcome(agent_result)
            passed = actual == case["expected_outcome"]
            results.append({
                "input": case["input"],
                "category": case["category"],
                "expected": case["expected_outcome"],
                "actual": actual,
                "passed": passed,
                "response": agent_result["response"][:200],
            })
            print(f"  Expected: {case['expected_outcome']}, Got: {actual} {'✓' if passed else '✗'}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "input": case["input"],
                "category": case["category"],
                "expected": case["expected_outcome"],
                "actual": "error",
                "passed": False,
                "response": str(e),
            })
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} passed ({100*passed/total:.0f}%)")
    # Break down by category
    by_category = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"passed": 0, "total": 0}
        by_category[cat]["total"] += 1
        if r["passed"]:
            by_category[cat]["passed"] += 1
    print("\nBy category:")
    for cat, counts in by_category.items():
        print(f"  {cat}: {counts['passed']}/{counts['total']}")
    # Show failures
    failures = [r for r in results if not r["passed"]]
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for f in failures:
            print(f"\n  Input: {f['input']}")
            print(f"  Expected: {f['expected']}, Got: {f['actual']}")
            print(f"  Response: {f['response'][:150]}")
    return results

if __name__ == "__main__":
    run_evaluation()


