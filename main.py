from app1 import run_chat as travel_agent_1
from app2 import run_chat as travel_agent_2
from app3 import run_chat as travel_agent_3

def main_run():
    while True:
        print("Select a travel agent:")
        print("1. Travel Agent 1 (Food & Culture Spotlights)")
        print("2. Travel Agent 2 (Flight and Hotel Recommendations)")
        print("3. Travel Agent 3 (premium (connected)")
        print("4. Exit")

        choice = input("Enter the number of the travel agent you want to use (1, 2, 3, or 4): ")

        if choice == '1':
            travel_agent_1()
        elif choice == '2':
            travel_agent_2()
        elif choice == '3':
            travel_agent_3()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select either 1, 2, or 3.")
main_run()