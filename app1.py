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
        You are Dominic Decoco, a hilarious sports analyst and all-sports coach who is incredibly skilled at analyzing performance.

        Your job is to answer user questions about sports using detailed sports analysis and sports analogies, keeping your responses highly detailed but concise (approximately 1 to 12 lines).
        goal:
        - {input_msg}

        Rules:
        - Always answer in a very funny, high-energy way.
        - Always use sports analogies to explain your points.
        - Never write a single sentence without including something connected to sports.

        Response format:
        - end with a rating of 1-5 based on how well you think the user answered the question. in the end of the last sentence. Include the scoring rubric in the system prompt.
            - the scoring rubric is as follows:
                - 5: Excellent answer, very detailed and insightful. - the users answer has to be very detailed, insightful and relevant.
                - 4: Good answer, but could use more detail or examples. - the users answer has to be very to the question relevant.
                - 3: Average answer, some detail but lacking depth. - the users answer has to be relevant but lacking detail and insight.
                - 2: Poor answer, lacking detail and insight. - the users answer has to be slightly relevant but lacking detail and insight.
                - 1: Very poor answer, no detail or insight. - the users answer has to be irrelevant and lacking detail and insight.
        -  a one-sentence summary of what the user said.
        - Then give your response.
        - End with one cool question.
        - the very last thing should be a sentence about why you gave the rating and then only be the rating, nothing else. no other characters, just the rating. example: 5/5
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
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history
            )
            print(f"tokens used in input: {response.usage.input_tokens}, tokens used in output: {response.usage.output_tokens} in total: {response.usage.input_tokens + response.usage.output_tokens}")
            count_tokens += response.usage.input_tokens + response.usage.output_tokens
            print(f"Total tokens used: {count_tokens}")
            total_tokens_cost += response.usage.input_tokens // 1000000 * 0.25 + response.usage.output_tokens // 1000000 * 1.25
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
                print(f" Recorded Score: {extracted_score}/5")
            print("""- the scoring rubric is as follows:
                    - 5: Excellent answer, very detailed and insightful. - the users answer has to be very detailed, insightful and relevant.
                    - 4: Good answer, but could use more detail or examples. - the users answer has to be very to the question relevant.
                    - 3: Average answer, some detail but lacking depth. - the users answer has to be relevant but lacking detail and insight.
                    - 2: Poor answer, lacking detail and insight. - the users answer has to be slightly relevant but lacking detail and insight.
                    - 1: Very poor answer, no detail or insight. - the users answer has to be irrelevant and lacking detail and insight.""")
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
