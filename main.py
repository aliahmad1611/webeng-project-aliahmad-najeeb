import flet as ft
from views.engine_d_chat import create_chat_engine

def main(page: ft.Page):
    # --- 1. PAGE CONFIGURATION ---
    page.title = "AvianQuest"
    page.theme_mode = ft.ThemeMode.DARK 
    page.window.width = 400
    page.window.height = 800
    page.padding = 0
    page.spacing = 0

    # --- 2. ENGINE INITIALIZATION ---
    def create_placeholder(text, color):
        return ft.Container(
            expand=True,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=100, height=100, bgcolor=color, border_radius=25,
                        content=ft.Icon(ft.Icons.CONSTRUCTION, color="white", size=40)
                    ),
                    ft.Text(text, size=22, weight="bold", text_align="center")
                ]
            )
        )

    engine_a = create_placeholder("Routine Tracker", "#58CC02")
    engine_b = create_placeholder("Avian Lessons", "#FFC800")
    engine_c = create_placeholder("Avian Eye AI", "#CE82FF")
    engine_d = create_chat_engine(page)
    engine_e = create_placeholder("Risk Predictor", "#FF4B4B")

    # --- 3. MAIN DISPLAY AREA ---
    main_display = ft.Container(content=engine_d, expand=True)

    # --- 4. NAVIGATION LOGIC ---
    def on_nav_change(e):
        index = e.control.selected_index
        if index == 0:
            main_display.content = engine_a
        elif index == 1:
            main_display.content = engine_b
        elif index == 2:
            main_display.content = engine_c
        elif index == 3:
            main_display.content = engine_d
        elif index == 4:
            main_display.content = engine_e
        page.update()

    # --- 5. ADVANCED NAVIGATION BAR ---
    page.navigation_bar = ft.NavigationBar(
        selected_index=3, 
        bgcolor="#1A1A2E",
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CHECK_BOX_OUTLINED, selected_icon=ft.Icons.CHECK_BOX, label="Routine"),
            ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK_OUTLINED, selected_icon=ft.Icons.MENU_BOOK, label="Lessons"),
            ft.NavigationBarDestination(icon=ft.Icons.CAMERA_ALT_OUTLINED, selected_icon=ft.Icons.CAMERA_ALT, label="Avian Eye"),
            ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.Icons.CHAT_BUBBLE, label="Pocket Vet"),
            ft.NavigationBarDestination(icon=ft.Icons.SHOW_CHART, label="Risk"),
        ],
    )

    # --- 6. ADD TO PAGE ---
    page.add(main_display)

if __name__ == "__main__":
    # ⚡ FIXED: Modern entry point for Flet >= 0.80.0
    ft.run(main)