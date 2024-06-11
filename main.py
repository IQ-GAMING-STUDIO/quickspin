import flet as ft
from flet import *
from images import *
import random
from randomiser import *
from amountOfWinning import *
import json
import os
import schedule
import time
from threading import Thread
import re

fruits = {"1": apple, "2": banana, "3": pear}

def MainPage(page: ft.Page) -> None:
    client_ip = page.client_ip
    secret_key = None

    def close_warning_dialog():
        page.dialog.open = False
        page.update()

    def is_valid_key(key):
        return re.match(r'^[a-z0-9]{4}-[a-z0-9]{4}$', key) is not None

    def enable_proceed_button(e):
        if is_valid_key(secret_key_input.value):
            proceed_button.disabled = False
        else:
            proceed_button.disabled = True
        proceed_button.update()

    def use_existing_key(e):
        nonlocal secret_key
        secret_key = secret_key_input.value
        data_filename = f"data_{secret_key}.json"
        if not os.path.exists(data_filename):
            warning_text.value = "Secret key not found. Please try again or create a new one."
            warning_text.update()
        else:
            close_warning_dialog()
            load_main_interface(data_filename)

    def generate_secret_key():
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4)) + '-' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))

    def create_new_key(e):
        nonlocal secret_key
        secret_key = generate_secret_key()
        secret_key_display.value = f"Your new secret key is: {secret_key}"
        secret_key_display.update()
        data_filename = f"data_{secret_key}.json"
        with open(data_filename, 'w') as file:
            initial_data = {"min_to_out": 20, "balance": 3, "bet": 1}
            json.dump(initial_data, file)
        close_warning_dialog()
        load_main_interface(data_filename)

    if not client_ip:
        secret_key_input = ft.TextField(label="XXXX-XXXX", on_change=enable_proceed_button, width=200)
        warning_text = ft.Text(value="Use your secret-key", color=ft.colors.RED, size=20)
        proceed_button = ft.TextButton("Proceed", on_click=use_existing_key, disabled=True, width="200%")
        create_button = ft.TextButton("Create New Key", on_click=create_new_key, width="200%")
        secret_key_display = ft.Text(value="", size=20, color=ft.colors.GREEN)

        page.dialog = ft.AlertDialog(
            title=ft.Text("Warning"),
            content=ft.Column([
                ft.Text("We are not able to get your IP adress in order to create an account. You can use a secret-key instead.", size=20),
                ft.Text("Enter your existing secret-key or create a new one.", size=20),
                ft.Text("", size=20),
                secret_key_input,
                warning_text,
                secret_key_display
            ]),
            actions=[
                create_button,
                proceed_button
            ],
        )
        page.dialog.open = True
        page.update()
    else:
        data_filename = f"data_{client_ip}.json"


    def load_main_interface(data_filename):
        if not os.path.exists(data_filename):
            with open(data_filename, 'w') as file:
                initial_data = {"min_to_out": 20, "balance": 3, "bet": 1}
                json.dump(initial_data, file)

        with open(data_filename, 'r') as file:
            data = json.load(file)

        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        heading = ft.Text(value="Quick Spin", size=50, weight=ft.FontWeight.BOLD)

        page.add(
            heading,
            ft.Text(value="")
        )

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

        winning_amount = CalculateAmountOfWinning(apple_count, data_filename)
        winning_amount_text = ft.Text(value=str(winning_amount) + "$", size=30, color=ft.colors.BLACK,
                                      weight=ft.FontWeight.BOLD)

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

        balance_text = ft.Text(value=f"Balance: ${data['balance']}", size=30, color=ft.colors.WHITE,
                               weight=ft.FontWeight.BOLD)

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

                        new_winning_amount = CalculateAmountOfWinning(apple_count, data_filename)
                        winning_amount_text.value = str(new_winning_amount)
                        winning_amount_text.update()

                all_cards_revealed = all(card.button_clicked for card in card_controls)
                if all_cards_revealed:
                    with open(data_filename, 'r') as file:
                        data_temp = json.load(file)

                    data_temp["balance"] += CalculateAmountOfWinning(apple_count, data_filename)
                    balance_text.value = f"Balance: ${data_temp['balance']}"

                    with open(data_filename, 'w') as file:
                        json.dump(data_temp, file)

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
            given = RandomizeCards(data_filename)
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

        secret_key_text = ft.Text(value=secret_key, size=20, color=ft.colors.GREEN_50)

        page.add(ft.Text(""))
        page.add(ft.Text(value="You are playing on:", size = 15) , secret_key_text),

        def open_terms_of_use(e):
            ft.open_link("https://docs.google.com/document/d/18LIZE6cx2SvUa4FEVrc76KZZFXEJF3MoGOweurWMwXk/edit?usp=sharing")

        def open_privacy_policy(e):
            ft.open_link("https://docs.google.com/document/d/1qtNRVb_UWhOgfWwEj6-livdERiBhdXbsL0OOoPanHss/edit?usp=sharing")

        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        terms_of_use_button = ft.TextButton("Terms of Use", on_click=open_terms_of_use)
        privacy_policy_button = ft.TextButton("Privacy Policy", on_click=open_privacy_policy)

        page.add(ft.Text(""))

        page.add(
            ft.Row(
                controls=[
                    terms_of_use_button,
                    privacy_policy_button
                ],
                spacing=10,
                alignment=MainAxisAlignment.CENTER,
            ),
        )

        page.update()

def check_and_update_balances():
    for filename in os.listdir("/"):
        if filename.endswith(".json"):
            with open(filename, 'r') as file:
                data = json.load(file)
            if data["balance"] < 3:
                data["balance"] = 3
                with open(filename, 'w') as file:
                    json.dump(data, file)

def schedule_daily_update():
    schedule.every().day.at("00:00").do(check_and_update_balances)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    scheduler_thread = Thread(target=schedule_daily_update)
    scheduler_thread.daemon = True
    scheduler_thread.start()

ft.app(target=MainPage, assets_dir="assets")
