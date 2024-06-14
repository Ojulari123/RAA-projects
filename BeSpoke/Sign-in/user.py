import json
import datetime
import os

def ask_details():
    if os.path.exists("user.json"):
        with open("user.json", "r") as file:
            user = json.load(file)
    else:
        user = []

    print("\nSign-in Page")
    fname = input("Enter your first name: ")
    lname = input("Enter your last name: ")

    for user_id in user:
        ID = user_id["id"]

    while True:
        address = input("Enter your Email Address: ")
        password = input("Enter your password: ")

        time = datetime.datetime.now()
        timestamp = time.strftime("%y-%m-%d : %H:%M %p")


        if check_for_duplicate_email(address) == True:
            print("Email address is unavailable")
            
        else:
            print("Email address is Valid for use")
            ID += 1

            dic = {
                "id" : ID,
                "first_name": fname,
                "last_name": lname,
                "email": address,
                "password": password,
                "date registered" : timestamp
                }
            user.append(dic)

            with open("user.json", "w") as file:
                file.write(json.dumps(user, indent=4))
            print("\nuser successfully registered")
            break
        
def log_in():
    if os.path.exists("user.json"):
        with open("user.json", "r") as file:
            users = json.load(file)
    else:
        users = []

    tries = 0

    user_found = False
    matched_user = None
    while tries < 3:
        address = input("\nEnter your Email Address to sign-in: ")
        password = input("Enter your password to sign-in: ")
        for user in users:
            if (address == str(user["email"])) and (password == str(user["password"])): 
                print("Welcome!!")
                user_found = True
                matched_user = user
                break

        if user_found :
            break
        else:
            print("Wrong Info. Kindly try again :)")
        tries += 1

    if tries == 3:
        ask_details()
        log_in()


def check_for_duplicate_email(new_email):
    if os.path.exists("user.json"):
        with open("user.json", "r") as file:
            user_emails = json.load(file)
    else:
        return "File Not Found"

    for user in user_emails:
        existing_email = user.get("email")
        if new_email == existing_email:
            return True
            
    return False

    
def add_products():
    if os.path.exists("products.json"):
        with open("products.json", "r") as file:
            products = json.load(file)
    else:
        products = []

    ID = 1

    while True:
        ans = input("\nWould you like to add products?(y/n): ")
        if ans.lower() == "y": 
            product = input("Enter the product to be added: ")
            price = int(input("Enter the price of the product to be added: "))
            quantity = int(input("Enter the quantity to be added: "))

            ID += 1
            dic = {
                "id" : ID,
                "product": product,
                "price": price,
                "quantity": quantity,
                "user-ID" : ID
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
    ans = input("\nWould you like to print all the products added to the cart? (y/n)")
    if ans.lower() == "y":
        with open("products.json", "r") as file:
            products = json.load(file)
            print("\n")
            print("The added products are: ")
            print(products)
            total_price = sum(product['price'] * product['quantity'] for product in products)
            print(f"\nThe total of your cart is: {total_price}")
    
    elif ans == "n" or ans == "N":
        print("Have a nice day")
    else:
        print("Invalid Option, Try again")
        

def main():
    ask_details()
    log_in()
    add_products()
    print_products()

if __name__ == "__main__":
    main()



