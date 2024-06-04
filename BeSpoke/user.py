import json

def ask_details():
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


    json_object = json.dumps(dic, indent=4)

    with open("user.json", "w") as file:
        file.write(json_object)

def sign_in():
    address = input("\nEnter your Email Address to sign-in: ")
    password = input("Enter your password to sign-in: ")
    json_file = open("user.json", "r")
    json_read = json_file.read()
    obj = json.loads(json_read)

    if (address != str(obj["email"])) or (password != str(obj["password"])) :
        print("Wrong Info. Kindly try again :)")
        address = input("\nEnter your Email Address to sign-in: ")
        password = input("Enter your password to sign-in: ")
    else:
        print("Welcome!!")

def add_products():
    while True:
        ans = input("\nWould you like to add products?(y/n): ")
        if ans == "y" or ans == "Y":
            product = input("Enter the product to be added: ")
            price = input("Enter the price of the product to be added: ")
            quantity = input("Enter the quantity to be added:")
            dic = {
                "product": product,
                "price": price,
                "quantity": quantity
            }

            json_object = json.dumps(dic, indent=4)
            with open("products.json", "w") as file:
                file.write(json_object)

        elif ans == "n" or ans == "N":
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



