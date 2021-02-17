#!/usr/bin/env python3
import asyncio, datetime, sys, random
from vulcan import Keystore, Account, VulcanHebe
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

try:
    target_date = datetime.date.fromisoformat(sys.argv[1])
except:
    target_date = datetime.datetime.now()

grades = []
lessons = []
attendance = []

async def setup():
    global grades
    global lessons
    global attendance

    try:
        with open("keystore.json", 'r') as file:
            keystore = Keystore.load(file.read())
    except FileNotFoundError:
        print("No keystore found! Creating")
        keystore = Keystore.create()
    
    try:
        with open("account.json", 'r') as file:
            account = Account.load(file.read())
    except FileNotFoundError:
        print("No account registered!")
        token = input("Please, tell me your token: ")
        symbol = input("Next is your symbol: ")
        pin = input("And lastly, pin: ")
    
        account = await Account.register(keystore, token, symbol, pin)
        with open("account.json", 'w') as file:
            file.write(account.as_json)
    
    with open("keystore.json", "w") as file:
        file.write(keystore.as_json)

    client = VulcanHebe(keystore, account)
    await client.select_student()

    grades = await client.data.get_grades(date_from=target_date)
    tmp = []
    async for grade in grades:
        tmp.append(grade)

    grades = tmp

    lessons = await client.data.get_lessons(date_from=target_date)
    tmp = []
    async for lesson in lessons:
        tmp.append(lesson)

    lessons = tmp

    attendance = await client.data.get_attendance(date_from=target_date)
    tmp = []
    async for att in attendance:
        tmp.append(att)

    attendance = tmp
    
    await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Lp.", justify="right")
    table.add_column("Od")
    table.add_column("Do")
    table.add_column("Przedmiot")
    table.add_column("Obecność", justify="center")

    all_info = {}

    for lesson in lessons:
        if lesson.visible:
            all_info[lesson.time.position] = [lesson]
    for att in attendance:
        if att.time.position in all_info.keys():
            all_info[att.time.position].append(att)

    godziny_nieobecne = []
    for key in sorted(all_info):
        try:
            symbol = all_info[key][1].presence_type.symbol
            if symbol == "▬":
                symbol = "[red]" + symbol + "[/red]"
                godziny_nieobecne.append(str(all_info[key][1].time.position))
            elif symbol == "●":
                symbol = "[green]" + symbol + "[/green]"
            elif symbol == "s":
                symbol = "[yellow]" + symbol + "[/yellow]"
        except:
            symbol = "[dim]N/A[/dim]"

        name = all_info[key][0].subject.name
        if len(name) > 15:
            name = all_info[key][0].subject.code
            
        table.add_row("[green]" + str(all_info[key][0].time.position) + "[/green]", all_info[key][0].time.displayed_time.split("-")[0], all_info[key][0].time.displayed_time.split("-")[1], name, symbol)

    console.print(table)

    if len(godziny_nieobecne) > 0:
        # Generate excuse
        text = None
        if len(godziny_nieobecne) == 1:
            text = f'Proszę o usprawiedliwienie {godziny_nieobecne[0]} godziny lekcyjnej'
        elif len(godziny_nieobecne) > 1:
            text = 'Proszę o usprawiedliwienie godzin: ' + ', '.join(godziny_nieobecne)
        
        text += " z dnia " + str(target_date.strftime("%d.%m.%Y"))
    
        excuses = [' z powodu problemów z internetem.', ' z powodów rodzinnych.', '. Musiałem załatwić sprawę w urzędzie.', ', ponieważ miałem problemy z komputerem (Aktualizacja Windows\'a).', ', musiałem opiekować się bratem.']
        if len(godziny_nieobecne) > 1:
            excuses.append(", ponieważ byłem u lekarza")
        if text:
            text += random.choice(excuses)
            print(Panel(text, expand=False))
