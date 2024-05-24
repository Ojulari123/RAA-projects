def greet_user():
     name = input("Hello what is your name? ")
     print(f"Welcome, {name}\n")

def ask_age():
    current_year = 2024
    birth_year = int(input("Whats your DOB? "))
    age = current_year - birth_year
    print(f"Your age, {age}\n")

def show_instructions():
    print("These are the instructions on how to use this note taking program")
    print("\nInstructions:\n")
    print("To add a note, simply type your text and press Enter.\n")
    print("To exit the program, type 'exit' and press Enter.")

def add_notes():
    print("\nStart taking notes")
    with open("notes.txt","a") as file:
        while True:
            notes = input("Enter your note: ")
            if notes.lower() == 'exit':
                print("Exiting and saving your notes")
                break
            file.write(notes + "\n")
            print("Note added! Type 'exit' to quit or continue adding notes.")

def main():
    name = greet_user()
    ask_age()
    show_instructions()
    add_notes()

if __name__ == "__main__":
    main()
