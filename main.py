from app1 import run_chat as travel_agent_1
from app2 import run_chat as travel_agent_2
def main_run():
    print("Select a travel agent:")
    print("1. Travel Agent 1 (Food & Culture Spotlights)")
    print("2. Travel Agent 2 (Flight and Hotel Recommendations)")

    choice = input("Enter the number of the travel agent you want to use (1 or 2): ")

    if choice == '1':
        travel_agent_1()
    elif choice == '2':
        travel_agent_2()
    else:
        print("Invalid choice. Please select either 1 or 2.")
main_run()