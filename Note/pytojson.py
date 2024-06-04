import json

with open("notes.txt","r") as file:
    print_file = file.readlines()

output = open("notes.json","w")
json.dump(print_file, output)
output.close()