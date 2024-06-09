import flet as ft
from flet import *
from images import *
import random
from randomiser import *
from amountOfWinning import *
import json
import os

fruits = {"1": apple, "2": banana, "3": pear}

def MainPage(page: ft.Page) -> None:

    client_ip = page.client_ip
    data_filename = f"data_{client_ip}.json"

    # Проверьте, существует ли файл данных, если нет - создайте его
    if not os.path.exists(data_filename):
        with open(data_filename, 'w') as file:
            initial_data = {"min_to_out": 20, "balance": 3, "bet": 1}
            json.dump(initial_data, file)

    with open(data_filename, 'r') as file:
        data = json.load(file)

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    apple_count = 0
    apple_count_text = ft.Text(value="0", size=30, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)

    apple_card = ft.Card(
        content=ft.Container(
            content=ft.Row([
                ft.Image(src=fruits["1"], width=40, height=40),
                apple_count_text
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            ),
        ),
        width=120,
        height=60,
        color=ft.colors.INDIGO_700
    )

    winning_amount = CalculateAmountOfWinning(apple_count, page.client_ip)
    winning_amount_text = ft.Text(value=str(winning_amount) + "$", size=30, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)

    amount_of_winnings_card = ft.Card(
        content=ft.Container(
            content=ft.Row([
                winning_amount_text
            ],
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER
            ),
        ),
        width=120,
        height=60,
        color=ft.colors.INDIGO_700
    )

    balance_text = ft.Text(value=f"Balance: ${data['balance']}", size=30, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)

    bet_placed = False

    class ImageContainer(ft.UserControl):
        def __init__(self, initial_image, images) -> None:
            super().__init__()
            self.initial_image = initial_image
            self.images = images
            self.button_clicked = False
            self.image_widget = ft.Image(src=initial_image, width=50, height=50)

        def build(self) -> None:
            return ft.Container(
                content=self.image_widget,
                alignment=ft.alignment.center,
                width=60,
                height=60,
                bgcolor=ft.colors.INDIGO_700,
                border_radius=ft.border_radius.all(5),
                on_click=self.change_image
            )

        def change_image(self, e) -> None:
            nonlocal apple_count
            if bet_placed and not self.button_clicked and self.images:
                new_image = random.choice(self.images)
                self.image_widget.src = new_image
                self.images.remove(new_image)
                self.button_clicked = True
                self.update()

                if new_image == apple:
                    apple_count += 1
                    apple_count_text.value = str(apple_count)
                    apple_count_text.update()

                    new_winning_amount = CalculateAmountOfWinning(apple_count, page.client_ip)
                    winning_amount_text.value = str(new_winning_amount)
                    winning_amount_text.update()

            all_cards_revealed = all(card.button_clicked for card in card_controls)
            if all_cards_revealed:
                with open(data_filename, 'r') as file:
                    data = json.load(file)

                data["balance"] += CalculateAmountOfWinning(apple_count, page.client_ip)
                balance_text.value = f"Balance: ${data['balance']}"

                with open(data_filename, 'w') as file:
                    json.dump(data, file)

                apple_count = 0
                apple_count_text.value = "0"
                apple_count_text.update()
                winning_amount_text.value = "0"
                winning_amount_text.update()
                balance_text.update()

                bet_input.disabled = False
                bet_button.disabled = False
                bet_input.update()
                bet_button.update()

    def GetCards():
        items = []
        given = RandomizeCards(page.client_ip)
        for i in given:
            items.append(
                ImageContainer(
                    initial_image=question_mark,
                    images=[fruits[str(i)]]
                )
            )
        return items

    def ToRows(items, items_per_row):
        rows = []
        row = []
        for i, item in enumerate(items):
            row.append(item)
            if (i + 1) % items_per_row == 0:
                rows.append(ft.Row(controls=row, spacing=20))
                row = []
        if row:
            rows.append(ft.Row(controls=row, spacing=20))
        return rows

    def shuffle_cards():
        nonlocal card_controls
        card_controls = GetCards()
        cards.controls = ToRows(card_controls, 10)
        cards.update()

    card_controls = GetCards()
    cards = ft.Column(
        wrap=True,
        spacing=20,
        run_spacing=40,
        controls=ToRows(card_controls, 10),
        height=200,
    )

    bet_input = ft.TextField(label="Enter your bet", value="10", width=200)
    bet_button = ft.ElevatedButton(text="Bet", on_click=lambda e: place_bet())

    bet_error_text = ft.Text(value="", color=ft.colors.RED, size=20)

    def place_bet():
        nonlocal bet_placed
        bet_amount = int(bet_input.value)
        with open(data_filename, 'r') as file:
            data = json.load(file)

        if bet_amount < 1:
            bet_error_text.value = "The minimum bet is $1."
            bet_error_text.update()
        elif bet_amount > data["balance"]:
            bet_error_text.value = "You cannot bet more than your balance."
            bet_error_text.update()
        else:
            data["bet"] = bet_amount
            data["balance"] -= bet_amount
            with open(data_filename, 'w') as file:
                json.dump(data, file)

            bet_error_text.value = ""
            bet_error_text.update()

            balance_text.value = f"Balance: ${data['balance']}"
            balance_text.update()

            bet_placed = True
            bet_input.disabled = True
            bet_button.disabled = True
            bet_input.update()
            bet_button.update()
            shuffle_cards()

    page.add(cards)
    page.add(
        ft.Row(
            controls=[
                bet_input,
                bet_button,
                bet_error_text
            ],
            alignment=MainAxisAlignment.CENTER,
            vertical_alignment=CrossAxisAlignment.CENTER
        )
    )

    def withdrawal_clicked(e):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Withdrawal Information"),
            content=ft.Text("Withdrawal is available from 25$ and above"),
            actions=[ft.TextButton("OK", on_click=lambda e: close_withdrawal_dialog(e))]
        )

        page.dialog.open = True
        page.update()

    withdrawal_button = ft.ElevatedButton(text="Withdrawal", on_click=withdrawal_clicked)

    def close_withdrawal_dialog(e):
        page.dialog.open = False
        page.update()

    page.add(
        ft.Row(controls=[balance_text], alignment=MainAxisAlignment.CENTER, vertical_alignment=CrossAxisAlignment.START)
    )

    page.add(ft.Row(controls=[apple_card, amount_of_winnings_card], alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER), withdrawal_button)
    page.update()

ft.app(target=MainPage, assets_dir="assets")