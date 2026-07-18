import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit)')
    input_msg = input('what is your goal for today? ')
    system_message = f"""
        You are  johnny an adventurous, deeply knowledgeable local guide and experience curator. Your job is to build highly detailed, engaginglists of things to do in the destination the user is flying to.

        Your goal is to curate activities based on the user's destination:
        - {input_msg}

        Rules:
        - Use web search to look up current events, seasonal highlights, local weather, and top-rated attractions for the specified destination. Formulate search queries like "[Destination] travel guide hidden gems" or "[Destination] events in [Month/Year]".
        - Keep your tone vibrant, inspiring, and rich with local flavor. Keep your response detailed but organized (approx. 10 to 18 lines).
        - Avoid generic recommendations , instead of just saying "visit Paris," recommend "watching the sunset from the steps of Sacré-Coeur in Montmartre".

        Response format:
        - A one-sentence enthusiastic summary of the vibe of the destination the user is visiting.
        - Top Attractions (The Must-Sees): 2 highly rated, iconic spots with brief descriptions of why they are worth it.
        - Hidden Gems (The Local Secrets): 2 off-the-beaten-path locations or experiences that regular tourists miss.
        - Food & Culture Spotlights:1-2 highly rated local dishes or specific street markets/cafes to try.
        - End with one tailored question asking about their personal interests  (outdoor adventure, history, art, or nightlife) to customize their itinerary further.
        """
    history = []
    score = []

    count_tokens = 0
    total_tokens_cost = 0
    while True:
        user_input = input(f'Turn[{len(history)//2 + 1}] You: ')
        if len(user_input) == 0:
            print("Please enter a message.")
            continue
        else:
            if user_input.lower() == 'exit':
                break
            history.append({'role': 'user', 'content': user_input})
            if user_input.lower() == '/summary':
                summary = history[-1]['content'] if history else "No conversation history."
                user_input = f"Summarize the conversation so far: {summary}"

            response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            temperature=0.7,
            system=system_message,
            messages=history,
            tools=[{"type": "web_search_20250305"}] 
            )

            print(f"tokens used in input: {response.usage.input_tokens}, tokens used in output: {response.usage.output_tokens} in total: {response.usage.input_tokens + response.usage.output_tokens}")
            count_tokens += response.usage.input_tokens + response.usage.output_tokens
            print(f"Total tokens used: {count_tokens}")
            total_tokens_cost += response.usage.input_tokens / 1000000 * 0.25 + response.usage.output_tokens // 1000000 * 1.25
            print(f"Total tokens cost: {total_tokens_cost}$")
            reply = response.content[0].text
            #print(response)
            #if len(history) > 3:
                #print('History:', history)
                #six messages because each turn has a user and ai
            print(f'Claude: {reply}')
            score_match = re.search(r'\[SCORE:\s*([1-5])/5\]', reply)
            if score_match:
                extracted_score = int(score_match.group(1))
                score.append(extracted_score)
            history.append({'role': 'assistant', 'content': reply})
            if user_input.lower() == 'reset':
                history = []
                print("Conversation reset.")
            if user_input.lower() == 'score':
                print("Score history:")
                print(score)
            if user_input.lower() == 'history':
                print("Conversation history:")
                for turn in history:
                    role = turn['role']
                    content = turn['content']
                    print(f"{role.capitalize()}: {content}")
run_chat()
