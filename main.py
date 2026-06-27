from typing import TypedDict
from langgraph.graph import StateGraph, START,END
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel,Field

class State(TypedDict):
    mail:str
    airlines:str
    rate_per_kg:int
    fuel_fees:int

    pieces:int
    length_cm:int
    width_cm:int
    height_cm:int
    
    actual_weight_kg:int
    chargable_weight:int

    total_cost:int

class ingestion_class(BaseModel):
    pieces:int = Field(
        description="how many pieces are being shipped"
    )

    length_cm:int = Field(
        description="what is the length of the shipment in centimeters"
    )

    width_cm:int = Field(
        description="what is the width of the shipment in centimeters"
    )

    height_cm:int = Field(
        description="what is the height of the shipment in centimeters"
    )

    actual_weight_kg:int = Field(
        description="what is the actual weight of the shipment in kg"
    )

    airlines:str = Field(
        description="from which airlines is shipment being transported"
    )

    rate_per_kg:int = Field(
        description="what is rate per kg the airline is taking to transport"
    )

    fuel_fees:int = Field(
        description="what is the fuel charges that the airlines is taking"
    )

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite",temperature=0)
def ingestion(state:State):
    llm_with_structured_output = llm.with_structured_output(ingestion_class)
    system_message = SystemMessage(content="""""")
    message_for_ai = [system_message,HumanMessage(content=state["mail"])]
    response = llm_with_structured_output.invoke(message_for_ai)
    print("Extracting fake data...\nData extracted!")
    return {
        "airlines":response.airlines,
        "rate_per_kg":response.rate_per_kg,
        "fuel_fees":response.fuel_fees,
        "pieces":response.pieces,
        "length_cm":response.length_cm,
        "width_cm":response.width_cm,
        "height_cm":response.height_cm,
        "actual_weight_kg":response.actual_weight_kg
    }

def calculator(state:State):
    print("Calculating total cost...")
    dimensional_weight = ((state["length_cm"]*state["width_cm"]*state["height_cm"])/6000)*state["pieces"]
    chargable_weight = max(dimensional_weight,state["actual_weight_kg"])
    total_cost = (chargable_weight*state["rate_per_kg"]) + state["fuel_fees"]
    print("Cost Calculated!!")
    return {
        "chargable_weight":chargable_weight,
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
        "mail":"""Hey, we can secure space for your 3 pallets. Each pallet is 120cm long, 80cm wide, and 160cm high. The total actual weight of the shipment is 500kg. Our rate is $4 per kg with a $200 fuel fee."""
    }

    response = graph.invoke(initial_state)

    print(f"Result of graph execution\n{response}")