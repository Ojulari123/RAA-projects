import json
import os

def ask_details():
    if os.path.exists("user.json"):
        with open("user.json", "r") as file:
            user = json.load(file)
    else:
        user = []

    fname = input("Enter your first name: ")
    lname = input("Enter your last name: ")
    address = input("Enter your Email Address: ")
    password = input("Enter your password: ")

    dic = {
        "first_name": fname,
        "last_name": lname,
        "email": address,
        "password": password
        }
    user.append(dic)

    with open("user.json", "w") as file:
        file.write(json.dumps(user, indent=4))

def sign_in():
    if os.path.exists("user.json"):
        with open("user.json", "r") as file:
            user = json.load(file)
    else:
        user = []

    address = input("\nEnter your Email Address to sign-in: ")
    password = input("Enter your password to sign-in: ")

    if (address != str(user["email"])) or (password != str(user["password"])):
        print("Wrong Info. Kindly try again :)")
        address = input("\nEnter your Email Address to sign-in: ")
        password = input("Enter your password to sign-in: ")
    else:
        print("Welcome!!")

def add_products():
    if os.path.exists("products.json"):
        with open("products.json", "r") as file:
            products = json.load(file)
    else:
        products = []

    while True:
        ans = input("\nWould you like to add products?(y/n): ")
        if ans.lower() == "y":
            product = input("Enter the product to be added: ")
            price = input("Enter the price of the product to be added: ")
            quantity = input("Enter the quantity to be added:")

            dic = {
                "product": product,
                "price": price,
                "quantity": quantity
            }
            products.append(dic)

            with open("products.json", "w") as file:
                file.write(json.dumps(products, indent=4))


        elif ans.lower() == "n":
            print("Thank you for visiting my store :)")
            break
        else:
            print("Invalid Option, Try again")

def print_products():
    ans = input("\nWould you like to print all the products added to the card? (y/n)")
    if ans == "y" or ans == "Y":
        with open("products.json", "r") as file:
            json_object = json.load(file)
            print("\n")
            print("The added products are: ")
            print(json_object)

    elif ans == "n" or ans == "N":
        print("Have a nice day")
    else:
        print("Invalid Option, Try again")
        



def main():
    ask_details()
    sign_in()
    add_products()
    print_products()

if __name__ == "__main__":
    main()



