#apple DONE
#banana DONE
#pear DONE
#cherry
#watermelon
#pineapple
#orange


#bet = 100$
# -100$

#1 = 0
#2 = 0
#3 = 50% (+50$)
#4 = 75% (+75$)
#5 = 120% (+120$)
#6 = 200% (+200$)
#7 = 300% (+300$)
#8 = 500% (+75$)
#9 NO!!!!!!!

#___________________________________________
#same cards >= 9 NO !!!!!! UNREAL !!!!!!!!!|
#__________________________________________|

#min_to_out = 20$

import json
import random

def RandomizeCards() -> list:
    with open('data.json', 'r') as file:
        data = json.load(file)

    fruits = []

    # Calculate efficiency as the difference between min_to_out and balance
    efficiency = data["min_to_out"] - data["balance"]

    # Calculate the ratio of efficiency to the bet
    ratio = efficiency / data["bet"]

    # Set the initial number of apple cards in a row based on efficiency
    if ratio >= 1:
        apples_in_a_row = random.randint(1, 4)
    else:
        apples_in_a_row = random.randint(2, 6)


    # Generate apple cards
    for i in range(apples_in_a_row):
        fruits.append(1)

    # Generate other fruit cards until reaching a total of 20 cards
    while len(fruits) < 20:
        # If the balance is close to the minimum to cash out, user must not win on each draw
        if data["balance"] >= 20:
            fruit = random.choice([2, 3])  # Exclude apple
        else:
            fruit = random.randint(2, 3)  # Include all fruits

        fruits.append(fruit)


    random.shuffle(fruits)

    return fruits

# Test the function
print(RandomizeCards())