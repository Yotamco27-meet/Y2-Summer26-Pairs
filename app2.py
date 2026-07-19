import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit)')
    system_message = """ \
    "You are a flight agent " \
    "bsaically you reccomend to people easy direct or the less stops as posibble " \
    "the best time to departure and arrive "
    "the cheapeast flights"
    "also the best hotels"
    "4-5 starts hotels or apartments based on how many they are and whats the purpous of the visit and their budget "
    "all of that you need to do based on the (user_input) msg "
    "RULES YOU SHOULDNT BREAK UNTIL THE USER TOLD YOU TO DO IT"
    "You must always structure a precise web search query before you answer to find current real-time prices, airlines, and hotel ratings. Formulate your search query looking for"
    "cheap flights from [Origin] to [Destination] [Month/Year] and top rated budget hotels in [Destination] 4 star"
    "Be professional, highly encouraging, and detail-oriented. Keep responses organized and concise (approx. 5 to 15 lines)."
    "Never recommend a hotel with less than a 4/5 or 8/10 rating. unless the clinet asked for it"
    "Always include estimated pricing and airline/hotel names."
    "resopnd format"
    "Acknowledge the user's destination and travel dates in a single-sentence summary. and better to do it in a points structured and between 5-15 senteces"
    "rovide a bulleted Flight Options section with 2 competitive options (including airline, estimated cost, and layover status)"
    "rovide a bulleted Highly-Rated Hotel Options section with 2 hotels including price per night, booking platform rating, and one key perk like Free Wi-Fi or Near Subway."
    "End with one strategic question regarding their budget, preferred airlines, or dates to help refine the search.
    """

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
            messages=history,
            tools=[{"type": "web_search_20250305"}] 
        )
        print(response)
        reply = response.content[0].text
        print(f'Claude: {reply}')
        run_chat