import json
import os 

with open("notes.txt","r") as file:
   read_note = file.readlines()

note_data = {}
for note in read_note:
        parts = note.split(" : ", 1)
        timestamp = f"{parts[0]}"
        note_content = parts[1].strip()
        note_data[timestamp] = note_content
    
name = input("What is your name? ")
year = int(input("What is your year of birth? "))

dic = {
    "name" : name,
    "year_of_birth" : year,
    "notes": note_data
}

with open("notes.json","w") as file:
    file.write(json.dumps(dic, indent=4))
