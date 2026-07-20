import os  
import re  
from anthropic import Anthropic  
from dotenv import load_dotenv  

load_dotenv()  

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))  


def save_booking(details: str):
    with open("bookings.txt", "a") as f:
        f.write(f"{details}\n---\n")
    return "Success: Booking saved locally."


def run_chat():  
    print('You: (type exit to quit)')  
    input_msg = input('what is your goal for today? ')  
    system_message = f"""  
    You are johnny an adventurous, deeply knowledgeable local  
    guide and experience curator. Your job is to build highly detailed,  
    engaging lists of things to do in the destination the user is flying to.  

    Your goal is to curate activities based on the user's destination:  
    - {input_msg}  

    Rules:  
    - Use web search to look up current events, seasonal highlights, local weather, and top-rated attractions for the specified destination.
    - Keep your tone vibrant, inspiring, and rich with local flavor. Keep your response detailed but organized (approx. 10 to 18 lines).  
    - Avoid generic recommendations, instead of just saying "visit Paris," recommend "watching the sunset from the steps of Sacré-Coeur in Montmartre".  

    Response format:  
    - A one-sentence enthusiastic summary of the vibe of the destination the user is visiting.  
    - Top Attractions (The Must-Sees): 2 highly rated, iconic spots with brief descriptions of why they are worth it.  
    - Hidden Gems (The Local Secrets): 2 off-the-beaten-path locations or experiences that regular tourists miss.  
    - Food & Culture Spotlights: 1-2 highly rated local dishes or specific street markets/cafes to try.  
    - End with one tailored question asking about their personal interests to customize their itinerary further.  
    """  
    history = []  
    score = []  

    tools_config = [{
        "name": "save_booking",
        "description": "Saves a confirmed flight or hotel booking text block.",
        "input_schema": {
            "type": "object",
            "properties": {"details": {"type": "string", "description": "The travel details."}},
            "required": ["details"]
        }
    }]

    count_tokens = 0  
    total_tokens_cost = 0  

    while True:  
        user_input = input(f'\nTurn[{len(history)//2 + 1}] You: ')  
        if len(user_input) == 0:  
            print("Please enter a message.")  
            continue  
        
        if user_input.lower() == 'exit':  
            break  
        
        if user_input.lower() == 'reset':  
            history = []  
            print("Conversation reset.")  
            continue

        if user_input.lower() == 'score':  
            print("Score history:", score)  
            continue

        if user_input.lower() == 'history':  
            print("Conversation history:")  
            for turn in history:  
                print(f"{turn['role'].capitalize()}: {turn['content']}")
            continue

        if user_input.lower() == '/summary':  
            summary = history[-1]['content'] if history else "No conversation history."  
            user_input = f"Summarize the conversation so far: {summary}"  

        history.append({'role': 'user', 'content': user_input})  

        try:
            response = client.messages.create(  
                model="claude-3-5-haiku-latest",  
                max_tokens=600,  
                temperature=0.7,  
                system=system_message,  
                messages=history,
                tools=tools_config 
            )  

            # Accumulate token metrics
            count_tokens += response.usage.input_tokens + response.usage.output_tokens  
            total_tokens_cost += (response.usage.input_tokens / 1_000_000) * 0.25 + (response.usage.output_tokens / 1_000_000) * 1.25  

            # Handle Tool Calls Loop
            while response.stop_reason == "tool_use":
                history.append({'role': 'assistant', 'content': response.content})
                
                tool_results = []
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

                history.append({'role': 'user', 'content': tool_results})

                # Call API again with updated tool results
                response = client.messages.create(
                    model="claude-3-5-haiku-latest",
                    max_tokens=600,
                    system=system_message,
                    messages=history,
                    tools=tools_config
                )

                # Accumulate tokens for the tool continuation response
                count_tokens += response.usage.input_tokens + response.usage.output_tokens  
                total_tokens_cost += (response.usage.input_tokens / 1_000_000) * 0.25 + (response.usage.output_tokens / 1_000_000) * 1.25  

            # Extract final reply
            reply = "".join([block.text for block in response.content if block.type == 'text'])
            print(f'\nClaude: {reply}')  

            # Extract Score if present
            score_match = re.search(r'\[SCORE:\s*([1-5])/5\]', reply)  
            if score_match:  
                score.append(int(score_match.group(1)))  

            # Append assistant response to history
            history.append({'role': 'assistant', 'content': response.content})  

            # Print token stats
            print(f"\n[Tokens used in turn: {response.usage.input_tokens + response.usage.output_tokens} | Total Tokens: {count_tokens} | Total Cost: ${total_tokens_cost:.6f}]")

        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    run_chat()