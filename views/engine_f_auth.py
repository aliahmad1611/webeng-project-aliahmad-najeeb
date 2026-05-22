import flet as ft
from database import db_manager
import re

def create_auth_engine(page: ft.Page, on_login_success):
    
    db_manager.init_db()

    def show_error(message):
        snack = ft.SnackBar(content=ft.Text(message, color="white"), bgcolor="#FF4B4B")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def show_success(message):
        snack = ft.SnackBar(content=ft.Text(message, color="white"), bgcolor="#58CC02")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def is_valid_email(email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None

    def handle_register(e):
        name = reg_name.value.strip()
        email = reg_email.value.strip()
        password = reg_password.value.strip()
        
        if not name or not email or not password:
            show_error("Please fill in all fields.")
            return
            
        if not is_valid_email(email):
            show_error("Please enter a valid email address (e.g., user@example.com).")
            return
            
        success, message = db_manager.create_user(name, email, password)
        if success:
            show_success(message)
            main_container.content = login_view
            page.update()
        else:
            show_error(message)

    def handle_login(e):
        email = login_email.value.strip()
        password = login_password.value.strip()
        
        if not email or not password:
            show_error("Please enter email and password.")
            return
            
        if not is_valid_email(email):
            show_error("Please enter a valid email address.")
            return
            
        success, user_id, name = db_manager.verify_user(email, password)
        if success:
            db_manager.set_active_session(user_id, name)
            show_success(f"Welcome back, {name}!")
            on_login_success() 
        else:
            show_error("Invalid email or password.")

    login_email = ft.TextField(label="Email Address", prefix_icon=ft.Icons.EMAIL, border_color="#33FFFFFF")
    login_password = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True, border_color="#33FFFFFF")
    
    reg_name = ft.TextField(label="Full Name", prefix_icon=ft.Icons.PERSON, border_color="#33FFFFFF")
    reg_email = ft.TextField(label="Email Address", prefix_icon=ft.Icons.EMAIL, border_color="#33FFFFFF")
    reg_password = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True, border_color="#33FFFFFF")

    def change_view(e, view_name):
        if view_name == "login":
            main_container.content = login_view
        elif view_name == "register":
            main_container.content = register_view
        page.update()

    login_view = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column([
            ft.Container(height=60),
            ft.Icon(ft.Icons.PETS, size=60, color="#CE82FF"),
            ft.Text("Welcome Back", size=32, weight="w900", color="white"),
            ft.Text("Sign in to access your flock.", size=14, color="white70"),
            ft.Container(height=40),
            login_email,
            ft.Container(height=10),
            login_password,
            ft.Container(height=20),
            ft.ElevatedButton("Sign In", bgcolor="#CE82FF", color="#1A1A2E", width=float('inf'), height=50, on_click=handle_login),
            ft.Container(height=20),
            ft.OutlinedButton("Create an Account", style=ft.ButtonStyle(color="white"), width=float('inf'), height=50, on_click=lambda e: change_view(e, "register"))
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    register_view = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column([
            ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: change_view(e, "login")),
            ft.Text("Join AvianQuest", size=32, weight="w900", color="white"),
            ft.Text("Create your secure account today.", size=14, color="white70"),
            ft.Container(height=30),
            reg_name,
            ft.Container(height=10),
            reg_email,
            ft.Container(height=10),
            reg_password,
            ft.Container(height=20),
            ft.ElevatedButton("Create Account", bgcolor="#58CC02", color="white", width=float('inf'), height=50, on_click=handle_register),
        ])
    )

    main_container = ft.AnimatedSwitcher(
        content=login_view,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=300,
        expand=True
    )

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]),
        content=main_container
    )