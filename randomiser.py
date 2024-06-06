import json
import random
import flet as ft

def RandomizeCards(client_ip) -> list:
    with open(f'data_{client_ip}.json', 'r') as file:
        data = json.load(file)

    fruits = []

    efficiency = data["min_to_out"] - data["balance"]

    ratio = efficiency / data["bet"]

    if ratio >= 1:
        apples_in_a_row = random.randint(1, 4)
    else:
        apples_in_a_row = random.randint(2, 6)

    for i in range(apples_in_a_row):
        fruits.append(1)

    while len(fruits) < 20:
        if data["balance"] >= 20:
            fruit = random.choice([2, 3])
        else:
            fruit = random.randint(2, 3)

        fruits.append(fruit)


    random.shuffle(fruits)

    return fruits

