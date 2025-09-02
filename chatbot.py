from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END   # ✅ Correct for v0.6.6
from typing import TypedDict, Annotated, List
import operator
import os

# Setup Gemini API
# os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"   # <-- replace with your real key
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# Fallback responses when API is not available
fallback_responses = {
    "water_saving": "Here are some water conservation tips: Take shorter showers, fix leaks, use low-flow fixtures, water plants during cooler hours, and collect rainwater.",
    "clean_water": "To keep water clean: Avoid dumping chemicals, use eco-friendly products, maintain septic systems, and protect water sources from pollution.",
    "sanitation": "Good sanitation practices include: Proper waste disposal, handwashing, maintaining clean toilets, and preventing water contamination."
}

# --- State ---
class ChatbotState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_node: str

# --- Agents ---
def water_saving_agent(state: ChatbotState):
    print("---WaterSavingAgent: Processing request---")
    messages = state["messages"]
    last_message = messages[-1].content

    water_saving_info = {
        "shower": "Take shorter showers and install low-flow showerheads.",
        "toilet": "Check for leaks and install water-saving toilets.",
        "garden": "Use drip irrigation and water during cooler hours.",
        "laundry": "Only run washing machines with full loads.",
        "dishes": "Use a dishwasher for full loads; don't run tap while washing manually.",
        "leaks": "Check for leaks regularly; fix dripping taps.",
        "rainwater": "Harvest rainwater from rooftops for non-potable uses.",
        "greywater": "Recycle greywater for irrigation or toilet flushing.",
        "general": "Turn off taps when brushing teeth; use a pitcher in the fridge.",
    }

    response = None
    for keyword, info in water_saving_info.items():
        if keyword in last_message.lower():
            response = info
            break

    if not response:
        # Use fallback response instead of API call
        response = fallback_responses["water_saving"]

    return {"messages": messages + [AIMessage(content=response)], "next_node": END}


def clean_water_agent(state: ChatbotState):
    print("---CleanWaterAgent: Processing request---")
    messages = state["messages"]
    last_message = messages[-1].content

    clean_water_info = {
        "protect sources": "Properly dispose of hazardous waste; avoid excess fertilizers.",
        "pollution": "Don't dump chemicals into drains; reduce chemical use.",
        "purification": "Use boiling, filtration, or chemicals to purify water.",
        "storm drain": "Never dump into storm drains; they go to rivers and lakes.",
        "industrial waste": "Ensure industrial waste is treated before discharge.",
    }

    response = None
    for keyword, info in clean_water_info.items():
        if keyword in last_message.lower():
            response = info
            break

    if not response:
        # Use fallback response instead of API call
        response = fallback_responses["clean_water"]

    return {"messages": messages + [AIMessage(content=response)], "next_node": END}


def sanitation_agent(state: ChatbotState):
    print("---SanitationAgent: Processing request---")
    messages = state["messages"]
    last_message = messages[-1].content

    sanitation_info = {
        "importance": "Sanitation prevents diseases and improves community health.",
        "disease": "Poor sanitation spreads waterborne diseases like cholera.",
        "waste management": "Proper waste disposal avoids contamination.",
        "toilets": "Safe toilets reduce human waste contact.",
        "hygiene": "Handwashing and hygiene reduce illness spread.",
    }

    response = None
    for keyword, info in sanitation_info.items():
        if keyword in last_message.lower():
            response = info
            break

    if not response:
        # Use fallback response instead of API call
        response = fallback_responses["sanitation"]

    return {"messages": messages + [AIMessage(content=response)], "next_node": END}


def default_response_agent(state: ChatbotState):
    print("---DefaultResponseAgent: Fallback response---")
    messages = state["messages"]
    last_message = messages[-1].content

    # Use fallback response instead of API call
    response = "I'm a water conservation and sanitation bot. I can help you with questions about saving water, keeping water clean, and proper sanitation practices. Could you ask me something specific about water conservation, clean water, or sanitation?"

    return {"messages": messages + [AIMessage(content=response)], "next_node": END}


def router_agent(state: ChatbotState):
    print("---RouterAgent: Routing request---")
    messages = state["messages"]
    last_message = messages[-1].content.lower()

    if any(
        keyword in last_message
        for keyword in ["save water", "water usage", "rainwater", "shower", "toilet", "garden", "drip", "greywater", "leaks"]
    ):
        return {"messages": messages, "next_node": "water_saving"}
    elif any(
        keyword in last_message
        for keyword in ["clean water", "pollution", "purify", "drinking", "storm drain", "waste disposal"]
    ):
        return {"messages": messages, "next_node": "clean_water"}
    elif any(
        keyword in last_message
        for keyword in ["sanitation", "hygiene", "disease", "toilets", "wastewater"]
    ):
        return {"messages": messages, "next_node": "sanitation"}
    else:
        return {"messages": messages, "next_node": "default_response"}


# --- LangGraph ---
workflow = StateGraph(ChatbotState)
workflow.add_node("router", router_agent)
workflow.add_node("water_saving", water_saving_agent)
workflow.add_node("clean_water", clean_water_agent)
workflow.add_node("sanitation", sanitation_agent)
workflow.add_node("default_response", default_response_agent)

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    lambda state: state["next_node"],
    {
        "water_saving": "water_saving",
        "clean_water": "clean_water",
        "sanitation": "sanitation",
        "default_response": "default_response",
        END: END,
    },
)

# These agents now end the flow
workflow.add_edge("water_saving", END)
workflow.add_edge("clean_water", END)
workflow.add_edge("sanitation", END)
workflow.add_edge("default_response", END)

# Compile graph
app = workflow.compile()

# --- Chat Loop (only for testing in terminal) ---
def run_chatbot():
    print("Welcome to the Water Conservation & Sanitation Chatbot! (Type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        initial_state = {"messages": [HumanMessage(content=user_input)], "next_node": "router"}

        final_state = app.invoke(initial_state)
        last_bot_message = final_state["messages"][-1]
        print(f"Chatbot: {last_bot_message.content}")


if __name__ == "__main__":
    run_chatbot()
