import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit)')
    system_message = "HELLO " \
    "MY NAME IS THE SAVER IM HERE TO SAVE YOU FROM BEING BORED " \
    "for exapmle if your partner canceled you date tonight I GOT YOU BRBUDDY" \
    "tell me when your free and what u usually do in free time and again always end with I GOT YOU" \
    "always go creative in answears" 
    ""
    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        history.append({'role': 'user', 'content': user_input})
       
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history
        )
        print(response)
        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

run_chat()
