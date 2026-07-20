import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def save_booking(details: str):
    with open("bookings.txt", "a") as f:
        f.write(f"{details}\n---\n")
    return "Success: Booking saved locally."

def run_chat():
    print('WELCOME TO THE BEST FLIGHT AGENT.')
    
    
    system_message = """You are a flight agent. 
    Basically you recommend to people easy direct flights, or flights with the fewest stops possible.
    Provide the best time to departure and arrive, and the cheapest flights.
    Also recommend the best hotels (4-5 star hotels or apartments) based on how many guests there are, the purpose of the visit, and their budget.
    All of this must be based on the user's input message.
    
    RULES YOU SHOULDN'T BREAK:
    1. Structure a precise web search query before you answer to find current real-time prices, airlines, and hotel ratings. Formulate your search query looking for: "cheap flights from [Origin] to [Destination] [Month/Year] and top rated budget hotels in [Destination] 4 star".
    2. Be professional, highly encouraging, and detail-oriented. Keep responses organized and concise (approx. 5 to 15 lines).
    3. Never recommend a hotel with less than a 4/5 or 8/10 rating unless the client specifically asked for it.
    4. Always include estimated pricing and airline/hotel names.
    
    RESPONSE FORMAT:
    [Summary]: A single-sentence structured point acknowledging the user's destination and travel dates.
    [Response]: The main answer, including:
      - A bulleted Flight Options section with 2 competitive options (including airline, estimated cost, and layover status).
      - A bulleted Highly-Rated Hotel Options section with 2 hotels including price per night, booking platform rating, and one key perk like Free Wi-Fi or Near Subway.
    [Next Step]: One strategic question regarding their budget, preferred airlines, or dates to help refine the search."""

    
    tools_config = [{
        "name": "save_booking",
        "description": "Saves a confirmed flight or hotel booking text block.",
        "input_schema": {
            "type": "object",
            "properties": {"details": {"type": "string", "description": "The travel details."}},
            "required": ["details"]
        }
    }]

    history = []

    while True:
        user_input = input('\n>>> ')

        if user_input.lower() == 'exit':
            
            break
        
        history.append({'role': 'user', 'content': user_input})
     
        try:
            response = client.messages.create(
                model='claude-3-5-haiku-latest', 
                max_tokens=600,                  
                temperature=0.7,
                system=system_message,
                messages=history,
                tools=tools_config
            )

            
            if response.stop_reason == "tool_use":
                history.append({'role': 'assistant', 'content': response.content})
                tool_block = next(b for b in response.content if b.type == "tool_use")
                
                result = save_booking(details=tool_block.input.get("details"))

                response = client.messages.create(
                    model='claude-3-5-haiku-latest',
                    max_tokens=600,
                    system=system_message,
                    messages=[*history, {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_block.id, "content": result}]}]
                )
            
           
            reply = "".join([block.text for block in response.content if block.type == 'text'])
            print(f'\nClaude:\n{reply}')
            history.append({'role': 'assistant', 'content': reply})
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    run_chat()
