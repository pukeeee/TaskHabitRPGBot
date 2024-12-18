from random import choice

while True:
    try:
        pswrdlength = int(input("Enter the length of the password (from 1 to 99): "))
        if 1 <= pswrdlength <= 99:
            break
        else:
            print("-_-")
            print("Enter a value from 1 to 99")
    except ValueError:
        print("-_-")
        print("-_-")
        print("The length should be a number")
while True:
    specsign = input("Add special characters to the password? (yes/no): ")
    if specsign.lower() == "yes" or specsign.lower() == "no":
        break
    else:
        print("Enter 'yes' or 'no': ")

def pswrdgen(pswrdlength, specsign):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    pswrd = ""
    specchars = "!#$%&*+-/=?_~"
    if specsign == "yes":
        chars += specchars
        for _ in range(pswrdlength):
            pswrd += choice(chars)
    else:
        for _ in range(pswrdlength):
            pswrd += choice(chars)
    return pswrd

print("Password: ", pswrdgen(pswrdlength, specsign))