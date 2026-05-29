import flet as ft
from views.engine_a_routine import create_routine_engine
from views.engine_b_lessons import create_lessons_engine
from views.engine_c_avian_eye import create_avian_eye_engine
from views.engine_d_chat import create_chat_engine
from views.engine_e_risk import create_risk_engine  # ⚡ Added the import!
from views.engine_f_auth import create_auth_engine 
from views.engine_g_settings import create_settings_engine
from views.engine_h_onboarding import create_onboarding_engine
from database import db_manager

def main(page: ft.Page):
    page.title = "AvianQuest"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 800
    page.padding = 0

    def handle_logout():
        page.clean() 
        route_user() # Send back to router on logout

    def load_main_app():
        page.clean() 
        
        engine_a = create_routine_engine(page)
        engine_b = create_lessons_engine(page)
        engine_c = create_avian_eye_engine(page)
        engine_d = create_chat_engine(page)
        engine_e = create_risk_engine(page) # ⚡ Now it actually calls the engine!
        engine_g = create_settings_engine(page, handle_logout)

        def on_nav_change(e):
            index = e.control.selected_index
            main_content.content = tabs[index]
            page.update()

        tabs = [engine_a, engine_b, engine_c, engine_d, engine_e, engine_g]

        bottom_nav = ft.NavigationBar(
            selected_index=0,
            on_change=on_nav_change,
            bgcolor="#1A1A2E",
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.CHECK_BOX_OUTLINED, selected_icon=ft.Icons.CHECK_BOX, label="Routine"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK_OUTLINED, selected_icon=ft.Icons.MENU_BOOK, label="Lessons"),
                ft.NavigationBarDestination(icon=ft.Icons.CAMERA_ALT_OUTLINED, selected_icon=ft.Icons.CAMERA_ALT, label="Eye"),
                ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.Icons.CHAT_BUBBLE, label="Vet"),
                ft.NavigationBarDestination(icon=ft.Icons.SHOW_CHART_OUTLINED, selected_icon=ft.Icons.SHOW_CHART, label="Risk"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
            ]
        )

        main_content = ft.Container(content=tabs[0], expand=True)

        page.add(ft.Column([main_content, bottom_nav], spacing=0, expand=True))
        page.update()

    # The Traffic Controller
    def route_user():
        page.clean()
        active_user = db_manager.get_active_session()
        
        if active_user:
            user_id = active_user[0]
            
            # Check the database: Have they finished onboarding?
            is_onboarded = db_manager.check_onboarding_status(user_id)
            
            if is_onboarded:
                load_main_app() # Skip straight to dashboard
            else:
                # Show the Duolingo Quiz
                onboarding_view = create_onboarding_engine(page, route_user)
                page.add(onboarding_view)
        else:
            # Not logged in at all
            auth_view = create_auth_engine(page, route_user)
            page.add(auth_view)
            
        page.update()

    db_manager.init_db() 
    route_user()

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # ⚡ THE FIX: Updated to ft.AppView.WEB_BROWSER
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
