#!/usr/bin/env python3
import asyncio, datetime, sys, random
from vulcan import Keystore, Account, VulcanHebe
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from setup import setup

try:
    target_subject = sys.argv[1]
except:
    target_subject = None

grades = []
lessons = []

async def main():
    global grades
    global lessons
    global grades_sorted
    global subject_names

    client = await setup()

    grades = await client.data.get_grades()
    tmp = []

    # print(grades)
    # print(type(grades))

    async for grade in grades:
        tmp.append(grade)

    grades = tmp
    # print(grades)

    grades_sorted = {}
    subject_names = {}

    for gr in grades:
        if gr.column.subject.id in grades_sorted:
            grades_sorted[gr.column.subject.id].append(gr)
        else:
            grades_sorted[gr.column.subject.id] = [gr]
        subject_names[gr.column.subject.id] = {
                'name': gr.column.subject.name,
                'code': gr.column.subject.code,
                'position': gr.column.subject.position
            }

    lessons = await client.data.get_lessons()
    tmp = []
    async for lesson in lessons:
        tmp.append(lesson)

    lessons = tmp

    
    await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    if target_subject:
        # find by id:
        try:
            target_subject = int(target_subject)
        except ValueError:
            # TODO find by name or code
            sys.exit(1)

        table.add_column("Data")
        table.add_column("Nazwa")
        table.add_column("Kod")
        table.add_column("Waga")
        table.add_column("Ocena")

        for grade in grades_sorted[target_subject]:
            table.add_row(
                grade.date_created.date.strftime('%Y-%m-%d'),
                grade.column.name,
                grade.column.code,
                str(grade.column.weight),
                grade.content
            )

        print(Panel('[bold magenta]Przedmiot:[/bold magenta] ' + subject_names[target_subject]['name'], expand=False))

    else:
        table.add_column("ID")
        table.add_column("Przedmiot", justify="left")
        table.add_column("Oceny")

        for key in grades_sorted:
            grades_string = ''
            for gr in grades_sorted[key]:
                grades_string += gr.content + '  '

            table.add_row(str(key), subject_names[key]['name'], grades_string)


    console.print(table)
