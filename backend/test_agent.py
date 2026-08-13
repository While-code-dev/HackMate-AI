from agent_core.orchestrator import MasterOrchestrator


def main():
    print("=" * 60)
    print("HACKMATE AI - AGENT TEST")
    print("=" * 60)

    print("\nStarting orchestrator...")

    orchestrator = MasterOrchestrator()

    print("Orchestrator started successfully!")

    user_message = (
        "I am a CSE student interested in Artificial Intelligence. "
        "I am working with 3 teammates and we have intermediate "
        "technical experience."
    )

    chat_history = []

    print("\nSending message to AI...")
    print(f"User: {user_message}")

    result = orchestrator.process_message(
        user_message=user_message,
        history=chat_history
    )

    print("\n" + "=" * 60)
    print("AI RESPONSE")
    print("=" * 60)

    print("\nChat Reply:")
    print(result["chat_reply"])

    print("\nReady for Project Specification:")
    print(result["is_ready_for_spec"])

    if result["project_spec"]:
        print("\nProject Specification:")
        print(result["project_spec"])

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()