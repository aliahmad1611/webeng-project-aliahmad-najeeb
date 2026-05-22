import flet as ft
from database import db_manager

def create_settings_engine(page: ft.Page, on_logout):
    
    def handle_logout(e):
        db_manager.clear_active_session()
        on_logout()

    session = db_manager.get_active_session()
    current_user = session[1] if session else "Avian Owner"

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column([
            ft.Text("Settings", size=32, weight="w900", color="white"),
            ft.Text("Manage your account and app preferences.", color="white70"),
            ft.Container(height=30),
            
            ft.Container(
                bgcolor="#11FFFFFF",
                border_radius=15,
                padding=20,
                content=ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=50, color="#CE82FF"),
                    ft.Column([
                        ft.Text(current_user, size=20, weight="bold", color="white"),
                        ft.Text("Active Account", size=12, color="#58CC02")
                    ])
                ])
            ),
            
            ft.Container(expand=True), 
            
            ft.ElevatedButton(
                "Log Out", 
                icon=ft.Icons.LOGOUT, 
                bgcolor="#FF4B4B", 
                color="white", 
                width=float('inf'), 
                height=50, 
                on_click=handle_logout
            ),
            ft.Container(height=20) 
        ])
    )