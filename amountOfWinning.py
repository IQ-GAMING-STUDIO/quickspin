import json
import flet as ft

def CalculateAmountOfWinning(apples, client_ip) -> float:

    with open(f'data_{client_ip}.json', 'r') as file:
        data = json.load(file)

    winning_percentage = [0, 0, 0, 50, 75, 120, 200, 300, 500]

    if apples < 0 or apples >= len(winning_percentage):
        return 0.0

    percent_to_number = winning_percentage[apples] / 100

    result = data["bet"] * percent_to_number

    return result