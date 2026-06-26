from typing import TypedDict
from langgraph.graph import StateGraph, START,END

class State(TypedDict):
    mail:str
    total_weight:int
    airlines:str
    rate_per_kg:int
    fuel_fees:int

    total_cost:int

def ingestion(state:State):
    print("Extracting fake data...\nData extracted!")
    return {
        "total_weight":500,
        "airlines":"Delta",
        "rate_per_kg":5,
        "fuel_fees":50
    }

def calculator(state:State):
    print("Calculating total cost...")
    total_cost = (state["total_weight"] * state["rate_per_kg"]) + state["fuel_fees"]
    print("Cost Calculated!!")
    return {
        "total_cost":total_cost
    }

def manager(state:State):
    print("Agent 3 is reviewing the final quote...")
    print("-------------------------------------------------")
    print(f"FINAL QUOTE READY: {state['airlines']}")
    print(f"Total Cost: ${state['total_cost']}")
    print("-------------------------------------------------")

graph_builder = StateGraph(State)
graph_builder.add_node("ingestion",ingestion)
graph_builder.add_node("calculator",calculator)
graph_builder.add_node("manager",manager)

graph_builder.add_edge(START,"ingestion")
graph_builder.add_edge("ingestion","calculator")
graph_builder.add_edge("calculator","manager")

graph = graph_builder.compile()

if __name__ == "__main__":
    initial_state = {
        "mail":"Hey, we can ship your 3 pallets (120x80x160cm) for $5 per kg plus a $50 fuel fee."
    }

    response = graph.invoke(initial_state)

    print(f"Result of graph execution\n{response}")