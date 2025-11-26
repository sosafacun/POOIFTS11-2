#python libs
from typing import List, Tuple
from datetime import datetime
from math import ceil
import random
import time

#rich libs
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich.columns import Columns

#live search
from readchar import readkey

#data creation
from utils.year_builder import read_filtered, read_month



class RichUI:
    console = Console()

    #----------------------------------------------
    #----------------------------------------------
    #----------------MENUS--------------------
    #----------------------------------------------
    #----------------------------------------------
    @staticmethod
    def simple_menu(title: str, subtitle: str, items: List[Tuple[str, str]]):
        RichUI.show_loading_message(title)
        try:
            return RichUI._menu_core(title, subtitle, items)
        except Exception as e:
            RichUI.console.print(Panel(f"[red]Error creating menu: {e}[/red]"))
            RichUI.pause()

    #builds the Title panel. The one that's on top of any menu
    @staticmethod
    def make_panel(title: str, subtitle: str = "", color: str = "bright_blue"):
        text = f"[bold cyan]{title}[/bold cyan]"
        if subtitle:
            text += f"\n[dim]{subtitle}[/dim]"
        return Panel.fit(text, border_style=color)

    #builds the menu frames and gets the data as a Tuple list to send it over to the _menu_core
    @staticmethod
    def make_menu(items: List[Tuple[str, str]], border_color: str = "bright_green"):
        menu = Table(
            box=box.DOUBLE_EDGE,
            border_style=border_color,
            show_header=False,
            padding=(0, 2)
        )
        for key, desc in items:
            menu.add_row(f"[green]{key}[/green]", desc)
        return menu

    #----------------------------------------------
    #----------------------------------------------
    #----------------USER INPUT--------------------
    #----------------------------------------------
    #----------------------------------------------
    @staticmethod
    def _option_select(valid_keys, default_opt):
        return Prompt.ask(
            "\n[bold white]Select an option[/bold white]",
            choices=valid_keys,
            default=default_opt
        ).upper()
    
    @staticmethod
    def prompt_user(msg: str):
        RichUI.clear()
        panel = Panel.fit(
            f"[white]{msg}[/white]\n\n[dim]Enter value below[/dim]",
            border_style="bright_blue"
        )
        
        RichUI.center(panel)

        while True:
            value = Prompt.ask("[bold cyan]> [/bold cyan]").strip()
            if value:
                return value

            RichUI.warning_message("Field cannot be blank.")

    @staticmethod
    def confirm_action(message: str, subtitle: str):
        warning_panel = Panel.fit(
            f"[bold bright_yellow]WARNING[/bold bright_yellow]\n\n"
            f"[bold white]{message}[/bold white]\n\n"
            f"[dim]{subtitle}[/dim]\n\n"
            f"[cyan]Confirm? (Y/N)[/cyan]",
            border_style="bright_red"
        )

        RichUI.center(warning_panel)

        choice = Prompt.ask(
            "\n[bold white]Enter your choice[/bold white]",
            choices=["y", "n", "Y", "N"],
            default="Y"
        ).upper()

        RichUI.show_loading_message(". . .")
        return choice == "Y"
    
    @staticmethod
    def live_search(items, label="Search"):
        query = ""

        search_tables = [
            (
                item,
                f"{getattr(item, 'id', '')} {getattr(item, 'name', '')} {getattr(item, 'last_name', '')} {getattr(item, 'phone', '')}".lower()
            )
            for item in items
        ]

        with Live(refresh_per_second=30, console=RichUI.console):
            while True:
                RichUI.clear()

                panel = Panel.fit(
                    f"{label}: {query}\n(ENTER = select, BACKSPACE = delete, ESC = cancel)",
                    border_style="bright_blue"
                )
                RichUI.center(panel)

                results = [obj for obj, text in search_tables if query.lower() in text]

                table = Table(show_header=True, header_style="bold cyan", box=None)
                table.add_column("ID")
                table.add_column("Name")
                table.add_column("Phone")

                for obj in results[:10] if results else []:
                    table.add_row(
                        getattr(obj, "id", ""),
                        f"{getattr(obj, 'name', '')} {getattr(obj, 'last_name', '')}",
                        getattr(obj, "phone", "")
                    )

                if not results:
                    table.add_row("No results", "", "")

                RichUI.center(table)

                key = readkey()

                if key == "\r":
                    return results[0] if results else None

                if key == "\x1b":
                    return None

                if key in ("\x08", "\x7f"):
                    query = query[:-1]
                    continue

                if key.isprintable():
                    query += key
    
    @staticmethod
    def prompt_edit(label, old_value):
        response = Prompt.ask(f"{label} ([dim]{old_value}[/dim])", default=str(old_value))
        return response
        
    @staticmethod
    def edit_object(target, field_map):
        updates = {}
        for field_name, label in field_map:
            current_value = getattr(target, field_name, "")
            new_value = RichUI.prompt_edit(label, current_value)
            updates[field_name] = new_value
        
        return updates

    @staticmethod
    def pick_calendar_date(rows):
        RichUI._show_calendar(rows)

        valid_keys = {str(i+1): r["date"] for i, r in enumerate(rows)}

        choice = RichUI._option_select(list(valid_keys.keys()), default_opt="1")

        try:
            return datetime.strptime(valid_keys[choice], "%Y-%m-%d").date()
        except:
            return None
    
    @staticmethod
    def pick_employee(employee_list):
        if not employee_list:
            RichUI.warning_message("No employees available.")
            RichUI.pause()
            return None

        mapping = {str(i+1): e for i, e in enumerate(employee_list)}

        RichUI.clear()
        RichUI.center(RichUI.make_panel("Select Employee"))

        RichUI.show_cards_static(list(mapping.values()))

        choice = RichUI._option_select(list(mapping.keys()), default_opt="1")
        return mapping.get(choice)

    @staticmethod
    def pick_slots(slot_state: dict):

        slot_list = list(slot_state.keys())
        mapping = {str(i+1): slot for i, slot in enumerate(slot_list)}

        selected = set()

        while True:
            RichUI.clear()
            RichUI.center(RichUI.make_panel("Select Time Slot(s)"))

            panels = []
            for i, slot in enumerate(slot_list, start=1):
                state = slot_state[slot]
                is_selected = slot in selected

                if state != "free":
                    color = "red"
                elif is_selected:
                    color = "yellow"
                else:
                    color = "green"
                

                if state == "taken":
                    status_text = "[dim]Unavailable[/dim]"
                elif is_selected:
                    status_text = "[dim](selected)[/dim]"
                else:
                    status_text = f"[dim]{i}[/dim]"

                content = f"[bold]{slot}[/bold]\n\n{status_text}"
                panels.append(Panel(content, border_style=color, width=14, height=5))

            RichUI.center(Columns(panels, equal=True, expand=False))

            choice = RichUI.console.input(
                "\nPress number to toggle slot, or ENTER to confirm: "
            ).strip()

            if choice == "":
                break

            if choice in mapping:
                slot = mapping[choice]
                if slot_state[slot] == "free":
                    if slot in selected:
                        selected.remove(slot)
                    else:
                        selected.add(slot)
                else:
                    RichUI.warning_message("That slot is already taken.")
                    RichUI.pause()
            else:
                RichUI.warning_message("Invalid option.")
                RichUI.pause()

        return sorted(selected)
    
    #----------------------------------------------
    #----------------------------------------------
    #----------------LOADING BAR--------------------
    #----------------------------------------------
    #----------------------------------------------

    @staticmethod
    def show_loading_message(message: str):
        panel = Panel.fit(
            f"[bold cyan]Loading {message}[/bold cyan]",
            border_style="bright_blue"
        )

        RichUI.center(panel)
        RichUI._show_loading_bar()

    #----------------------------------------------
    #----------------------------------------------
    #----------------DISPLAY--------------------
    #----------------------------------------------
    #----------------------------------------------
    @staticmethod
    def show_paginated_cards(items):
        if not items:
            RichUI.warning_message("No records found.")
            RichUI.pause()
            return

        RichUI.show_loading_message(". . .")
        RichUI._paginate(items, 6)

    @staticmethod
    def show_cards_static(items):
        panels = RichUI._make_cards(items)
        RichUI.center(Columns(panels, equal=True, expand=True))
        
    @staticmethod
    def show_next_weeks():
        rows = read_filtered(datetime.now().year)
        RichUI.center(RichUI._build_two_week_panel(rows))
        RichUI.pause()

    @staticmethod
    def show_month():
        now = datetime.now()
        rows = read_month(now.year, now.month)
        RichUI.clear()
        RichUI.center(RichUI._build_month_panel(rows))
        RichUI.pause()

    #----------------------------------------------
    #----------------------------------------------
    #----------------STATIC OPS--------------------
    #----------------------------------------------
    #----------------------------------------------
    @staticmethod
    def clear():
        RichUI.console.clear()

    @staticmethod
    def center(obj):
        RichUI.console.print(Align.center(obj))

    @staticmethod
    def pause():
        RichUI.console.input(f"\n[dim]Press 'Enter' to continue . . .[/dim]")
    
    @staticmethod
    def throw_exception(msg,e):
        RichUI.console.print(Panel(f"[red]{msg}: {e}[/red]"))

    @staticmethod
    def warning_message(msg: str):
        RichUI.console.print(Panel(f"[red]{msg}[/red]"))

    @staticmethod
    def show_message(msg: str):
        RichUI.console.print(Panel(f"[white]{msg}[/white]", border_style="bright_blue"))
    
    #----------------------------------------------
    #----------------------------------------------
    #----------------PRIVATE METHODS--------------------
    #----------------------------------------------
    #----------------------------------------------
    @staticmethod
    def _show_calendar(rows):

        blocks = []
        current_row = []
        last_weekday = None

        for idx, entry in enumerate(rows, start=1):
            dt = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            weekday = dt.weekday()  # 0 = Mon

            # new calendar row when weekday resets
            if last_weekday is not None and weekday < last_weekday:
                blocks.append(current_row)
                current_row = []

            # weekend alignment (skip non-working days)
            while len(current_row) < weekday:
                current_row.append(
                    Panel(" ", width=14, height=6, border_style="dim")
                )

            weekday_name = dt.strftime("%a")  # Mon Tue Wed Thu Fri
            date_line = dt.strftime("%Y-%m-%d")

            # selection number (dimmed)
            selectable_index = f"[dim]{idx}[/dim]"

            content = Align.center(
                f"[bold]{weekday_name}[/bold]\n{date_line}\n{selectable_index}",
                vertical="middle"
            )

            tile = Panel(
                content,
                width=14,
                height=6,
                border_style="bright_blue"
            )

            current_row.append(tile)
            last_weekday = weekday

        if current_row:
            blocks.append(current_row)

        rendered_rows = [
            Columns(week, align="center", expand=False)
            for week in blocks
        ]

        RichUI.clear()
        RichUI.console.print(Group(*rendered_rows))

    @staticmethod
    def _make_cards(items):
        panels = []

        for obj in items:
            header_left, header_right = obj.card_header()
            header = f"{header_left:<15} | {header_right}"

            body_lines = [f"{label}: {value}" for label, value in obj.card_body()]
            body = "\n".join(body_lines)

            line = f"[cyan]{'─' * len(header)}[/cyan]"

            content = f"{header}\n{line}\n{body}"
            panels.append(Panel(content, border_style=obj.card_color()))

        return panels

    @staticmethod
    def _paginate(items, page_size):
        if not items:
            RichUI.warning_message("No items to display.")
            RichUI.pause()
            return

        pages = ceil(len(items) / page_size)
        index = 0

        while True:
            RichUI.clear()

            start = index * page_size
            chunk = items[start:start + page_size]

            panels = RichUI._make_cards(chunk)
            RichUI.center(Columns(panels, equal=True, expand=True))

            nav_text = f"[dim]Page {index+1}/{pages} | '.' next | ',' prev | 'Q' Go Back[/dim]"
            RichUI.console.print(f"\n{nav_text}")

            choice = Prompt.ask("", choices=[".", ",", "Q", "q"], default="Q")

            if choice.upper() == "Q":
                break

            if choice == "." and index < pages - 1:
                index += 1

            elif choice == "," and index > 0:
                index -= 1

    @staticmethod
    def _show_loading_bar():
        duration = random.uniform(0.5, 1.5)

        progress = Progress(
            BarColumn(),
            TimeRemainingColumn(),
            expand=False,
            console=RichUI.console
        )

        task = progress.add_task("", total=duration)
        centered = Align.center(progress)

        #since i need the bar centered, this will
        #refresh the display (cannot center AND have a progressive bar)
        with Live(centered, refresh_per_second=30, console=RichUI.console):
            start = time.perf_counter()
            while True:
                elapsed = time.perf_counter() - start
                if elapsed >= duration:
                    progress.update(task, completed=duration)
                    break

                progress.update(task, completed=elapsed)
                time.sleep(0.05)

        RichUI.clear()
    
    @staticmethod
    def _menu_core(title: str, subtitle: str, items: List[Tuple[str, str]]):
        RichUI.clear()
        RichUI.center(RichUI.make_panel(title, subtitle))
        menu = RichUI.make_menu(items)
        RichUI.center(menu)

        valid_keys = [key.lower() for key, _ in items]

        return RichUI._option_select(valid_keys, "Q")