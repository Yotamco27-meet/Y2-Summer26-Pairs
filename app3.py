import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def save_booking_pdf(content: str) -> str:
    """Creates a PDF file with title and booking details all in one text string."""
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Travel Booking Confirmation", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Main Content
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, content)

    output_filename = "booking_confirmation.pdf"
    pdf.output(output_filename)
    return f"Success: Booking saved to {output_filename}"





# Shared Booking Tool
def save_booking(details: str):
    with open("bookings.txt", "a") as f:
        f.write(f"{details}\n---\n")
    return "Success: Booking saved locally."


TOOLS_CONFIG = [{
    "name": "save_booking",
    "description": "Saves a confirmed flight or hotel booking text block.",
    "input_schema": {
        "type": "object",
        "properties": {"details": {"type": "string", "description": "The travel details."}},
        "required": ["details"]
    }
}]


def connect_run_chat(system_prompt: str, history: list, max_tokens: int = 600) -> str:
    """Helper function to execute an agent call and handle tool execution loops."""
    # Create a shallow copy of history so agents don't mutate external lists unintentionally
    turn_history = list(history)

    response = client.messages.create(
        model='claude-4-5-haiku-latest',
        max_tokens=max_tokens,
        temperature=0.7,
        system=system_prompt,
        messages=turn_history,
        tools=TOOLS_CONFIG
    )

    # Handle Tool Use Loop
    while response.stop_reason == "tool_use":
        turn_history.append({'role': 'assistant', 'content': response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                res = save_booking(details=block.input.get("details")) if block.name == "save_booking" else "Error"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": res
                })

        turn_history.append({'role': 'user', 'content': tool_results})

        response = client.messages.create(
            model='claude-4-5-haiku-latest',
            max_tokens=max_tokens,
            system=system_prompt,
            messages=turn_history,
            tools=TOOLS_CONFIG
        )

    return "".join([block.text for block in response.content if block.type == 'text'])


def run_chat():
    print("=" * 60)
    print("AGENTS CONNECTED: Flight/Hotel Specialist 🤝 Local Guide Johnny")
    print("=" * 60)
    print("Type your message or travel goals below (type 'exit' to quit).\n")

    # Main multi-turn conversation history visible to the user
    conversation_history = []
    
    # Internal agent state tracking
    latest_logistics = "No flight/hotel context gathered yet."

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'exit':
            print("Ending session. Safe travels!")
            break

        if user_input.lower() == 'reset':
            conversation_history = []
            latest_logistics = "No flight/hotel context gathered yet."
            print("Conversation reset.")
            continue

        # Append latest user prompt to history
        conversation_history.append({'role': 'user', 'content': user_input})

        try:
            print("\n[Agent 2: Flight & Hotel Specialist Analyzing...]")
            
            # -------------------------------------------------------------
            # STEP 1: Agent 2 evaluates user input and history for logistics
            # -------------------------------------------------------------
            agent2_system = """You are a flight and hotel agent.
            Analyze the user input and full conversation history. 
            Identify or update flight recommendations and 4-5 star hotels based on budget/destination/dates.
            If user asks to save a booking, use the save_booking tool.
            
            Keep your response structured:
            - Flight Options (2 choices with airline, price, layovers)
            - Hotel Options (2 choices with price, ratings, location neighborhood)
            - Selected Primary Hotel & Neighborhood
            """

            latest_logistics = connect_run_chat(agent2_system, conversation_history, max_tokens=600)

            print("\n[Agent 1: Local Guide Johnny Planning Activities...]")

            # -------------------------------------------------------------
            # STEP 2: Agent 1 uses Agent 2's output to build local plans
            # -------------------------------------------------------------
            agent1_system = f"""You are Johnny, an adventurous local guide experience curator.
            
            CURRENT FLIGHT & HOTEL CONTEXT FROM AGENT 2:
            -------------------------------------------
            {latest_logistics}
            -------------------------------------------

            Your Task:
            - Build vibrant activity plans, hidden gems, and dining options centered around the destination and hotel neighborhood selected by Agent 2.
            - Ensure activities are specific, authentic local experiences (not generic tourist advise).
            - End with a strategic follow-up question to help refine the itinerary further.
            """

            # Feed conversation history to Johnny so he understands follow-up questions
            johnny_response = connect_run_chat(agent1_system, conversation_history, max_tokens=700)

            # STEP 3: Display combined response and update global history

            print("\n" + "=" * 60)
            print(" FLIGHT & HOTEL LOGISTICS (Agent 2):")
            print("-" * 60)
            print(latest_logistics)

            print("\n LOCAL EXPERIENCE & ITINERARY (Agent 1 - Johnny):")
            print("-" * 60)
            print(johnny_response)
            print("=" * 60)

            # Append assistant turn to history combining both insights
            full_combined_turn = f"LOGISTICS:\n{latest_logistics}\n\nITINERARY:\n{johnny_response}"
            conversation_history.append({'role': 'assistant', 'content': full_combined_turn})

        except Exception as e:
            print(f"\nAn error occurred during agent collaboration: {e}")


if __name__ == "__main__":
    run_chat()