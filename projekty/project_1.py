"""
project_1: the first project for the Engeto Online Python Academy

author = Adam Seifert
email: seifert.promotion@gmail.com
"""
TEXTS = ["""
Situated about 10 miles west of Kemmerer,
Fossil Butte is a ruggedly impressive
topographic feature that rises sharply
some 1000 feet above Twin Creek Valley
to an elevation of more than 7500 feet
above sea level. The butte is located just
north of US 30N and the Union Pacific Railroad,
which traverse the valley. """,
"""At the base of Fossil Butte are the bright
red, purple, yellow and gray beds of the Wasatch
Formation. Eroded portions of these horizontal
beds slope gradually upward from the valley floor
and steepen abruptly. Overlying them and extending
to the top of the butte are the much steeper
buff-to-white beds of the Green River Formation,
which are about 300 feet thick.""",
"""The monument contains 8198 acres and protects
a portion of the largest deposit of freshwater fish
fossils in the world. The richest fossil fish deposits
are found in multiple limestone layers, which lie some
100 feet below the top of the butte. The fossils
represent several varieties of perch, as well as
other freshwater genera and herring similar to those
in modern oceans. Other fish such as paddlefish,
garpike and stingray are also present."""
]
# Users and passwords in dict
users = {
    "bob": "123",
    "ann": "pass123",
    "mike": "password",
    "liz": "pass123"
}
# Loop for user login
SEP = ("-" * 40)
for _ in range(3):
    username = input("username: ").strip()
    password = input("password: ").strip()
    print(SEP)
    # Check if both username and password are provided
    if not username or not password:
        print("Both username and password are required!")
        continue
    # Check if the username starts with a lowercase letter
    if not username[0].islower():
        print("Username must start with a lowercase letter!")
        continue
    # Check if the user exists
    if  username not in users:
        print(f"username:{username}\npassword:{password}\nUnregistered user, terminating the program!")
        exit()
    # Check if the password is correct
    if users[username] != password:
        print(f"username:{username},\npassword:{password}\nIncorrect password, terminating the program!")
        exit()
    # Successful login
    print(f"Hello {username}, welcome to the app!\nWe have {len(TEXTS)} texts to be analyzed.")
    print(SEP)
    break  
else:
    print(f"\nusername:{username}\npassword:{password}\nAccess denied! Too many failed attempts, terminating the program!")
    exit()
text_num = input("Enter a number btw. 1 and 3 to select:").strip()
print(SEP)
# Text num definitions
if not text_num.isdigit() or int(text_num) not in range(1, 4):
    print("Invalid input. Terminating the program!")
    exit()
# Selection of a specific text
selected_text = TEXTS[int(text_num) - 1]
# Text analysis
words = selected_text.split()  
num_words = len(words)
num_titlecase = sum(word.istitle() for word in words)
num_uppercase = sum(word.isupper() and word.isalpha() for word in words)
num_lowercase = sum(word.islower() for word in words)
num_numeric = sum(word.isdigit() for word in words)
sum_numeric = sum(int(word) for word in words if word.isdigit())
# Analysis results
print(f"There are {num_words} words in the selected text.")
print(f"There are {num_titlecase} titlecase words.")
print(f"There are {num_uppercase} uppercase words.")  
print(f"There are {num_lowercase} lowercase words.")
print(f"There are {num_numeric} numeric strings.")
print(f"The sum of all the numbers {sum_numeric}")
print(SEP)
# Word length chart
word_lengths = {}
for word in words:
    word = word.strip(".,!?")  
    length = len(word)
    word_lengths[length] = word_lengths.get(length, 0) + 1
print(f"{'LEN':<3}|{'OCCURENCES':^15}|{'NR.':>3}")
print(SEP)
for length, count in sorted(word_lengths.items()):
    print(f"{length:<3}| {'*' * count:<15} |{count}")

