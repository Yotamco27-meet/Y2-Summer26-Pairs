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
    
    system_message = """You are a flight agent...""" # Keep your system prompt here

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

            # Keep looping while Claude wants to use tools
            while response.stop_reason == "tool_use":
                # 1. Append the assistant message containing tool_use blocks to history
                history.append({'role': 'assistant', 'content': response.content})
                
                tool_results = []

                # 2. Process all tool calls in the response
                for block in response.content:
                    if block.type == "tool_use":
                        if block.name == "save_booking":
                            result = save_booking(details=block.input.get("details"))
                        else:
                            result = "Error: Unknown tool."

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # 3. Append the tool results as a single user message into history
                history.append({'role': 'user', 'content': tool_results})

                # 4. Request the next turn from Claude with updated history
                response = client.messages.create(
                    model='claude-3-5-haiku-latest',
                    max_tokens=600,
                    system=system_message,
                    messages=history,
                    tools=tools_config
                )

            # Extract final text answer
            reply = "".join([block.text for block in response.content if block.type == 'text'])
            print(f'\nClaude:\n{reply}')
            
            # Save final assistant response into history
            history.append({'role': 'assistant', 'content': response.content})
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    run_chat()
