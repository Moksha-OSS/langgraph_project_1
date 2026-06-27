from typing import TypedDict
from langgraph.graph import StateGraph, START,END
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel,Field

class State(TypedDict):
    mail:str
    total_weight:int
    airlines:str
    rate_per_kg:int
    fuel_fees:int

    total_cost:int

class ingestion_class(BaseModel):
    total_weight:int = Field(
        description="from the mail find out the total weight of the shipment"
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
        "total_weight":response.total_weight,
        "airlines":response.airlines,
        "rate_per_kg":response.rate_per_kg,
        "fuel_fees":response.fuel_fees
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
        "mail":"""Subject: RE: Quote Request - Pallets to DXB

Hi team, 

Thanks for reaching out. We can secure space for your shipment on Lufthansa. 

Based on the dimensions provided, the total weight of your cargo is confirmed at 800 kg. Our standard transportation rate for this lane is $4 per kg. Please note that due to current market conditions, there is also a flat fuel fee of $200 applied to all shipments. 

Let me know if you want to lock this in before Friday. 

Best,
Dave"""
    }

    response = graph.invoke(initial_state)

    print(f"Result of graph execution\n{response}")