from datetime import datetime
from datetime import date
import os
import json

def greet_user():
     print("Welcome!!!\n")

def show_instructions():
    print("These are the instructions on how to use this note taking program")
    print("\nInstructions:\n")
    print("To add a note, simply type your text and press Enter.\n")
    print("To exit the program, type 'exit' and press Enter.")

def add_notes():
    if os.path.exists("notes.json"):
         with open("notes.json","r") as file:
            read_note = json.load(file)
            if "notes" not in read_note:
                read_note = {
                    "notes" : []
                }
            
    else:
        read_note = {
            "notes" : []
        }
   
    name = input("Enter your name: ")
    year_of_birth = int(input("Enter your DOB: "))

    read_note["name"] = name
    read_note["DOB"] = year_of_birth
    
    while True:
        notes = input("Start taking notes: ")

        if notes.lower() == "exit":
            print("Exiting and saving your note")
            break
        time = datetime.now()
        timestamp = time.strftime("%y-%m-%d : %H:%M %p")
        user_note = {
            timestamp : notes
        }
        read_note["notes"].append(user_note)
        print("Note added! Type 'exit' to quit or continue adding notes.")

    with open("notes.json","w") as file:
        file.write(json.dumps(read_note, indent=4))
    
def print_notes():
        print("These are all your notes: \n")
        with open("notes.json","r") as file:
           note_data = json.load(file)
           print(note_data)
def main():
    greet_user()
    show_instructions()
    add_notes()
    print_notes()

if __name__ == "__main__":
    main()
