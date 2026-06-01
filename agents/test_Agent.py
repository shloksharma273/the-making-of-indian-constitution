# test_agent.py

from agents.constitution_agent import agent


while True:

    query = input("\nQuestion: ")

    result = agent.invoke(
        {
            "query": query
        }
    )

    print("\n")
    print(result["answer"])