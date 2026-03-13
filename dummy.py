import flet as ft
import json

def main(page: ft.Page):
    page.title = "AvianQuest"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 800
    
    # Center everything on the screen naturally
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # ==========================================
    # SINGLE PAGE APPLICATION (SPA) ARCHITECTURE
    # ==========================================

    def show_dashboard():
        page.clean() # Wipes the screen instantly
        page.add(
            ft.Icon(icon=ft.Icons.FAVORITE, size=80, color=ft.Colors.BLUE_600),
            ft.Text("AvianQuest", size=32, weight="bold", color=ft.Colors.BLUE_800),
            ft.Text("Certification Progress", size=16, color=ft.Colors.GREY_700),
            ft.ProgressBar(value=0.62, width=300, color=ft.Colors.GREEN, bgcolor=ft.Colors.GREY_200),
            ft.Text("310 / 500 Points", size=24, weight="bold"),
            ft.Container(height=30),
            
            # Using explicitly declared ft.Text() inside the content property
            ft.Button(
                content=ft.Text("Daily Care Routine", size=18), 
                icon=ft.Icons.CHECK_BOX, width=280, height=60, 
                on_click=lambda _: show_routine()
            ),
            ft.Container(height=10),
            ft.Button(
                content=ft.Text("Take GenAI Quiz", size=18), 
                icon=ft.Icons.LIGHTBULB, width=280, height=60, 
                on_click=lambda _: show_quiz()
            )
        )

    def show_routine():
        def finish_care(e):
            btn_care.content = ft.Text("Care Logged! ✅", size=18)
            btn_care.disabled = True
            status_text.value = "AI Prediction: Optimal Health 🟢"
            page.update()

        btn_care = ft.Button(
            content=ft.Text("Feed & Water Bird", size=18), 
            icon=ft.Icons.RESTAURANT, width=280, height=60, 
            on_click=finish_care
        )
        status_text = ft.Text("AI Status: Pending...", size=18, weight="bold")

        page.clean()
        page.add(
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: show_dashboard()),
                ft.Text("Daily Care", size=24, weight="bold")
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=20),
            ft.Text("Morning Tasks", size=28, weight="bold"),
            ft.Container(height=30),
            btn_care,
            ft.Container(height=20),
            status_text
        )

    def show_quiz():
        quiz_data = json.loads('{"question": "Which of these foods is toxic to parrots?","options": [{"text": "Spinach", "visual": "🥬"},{"text": "Blueberries", "visual": "🫐"},{"text": "Chocolate", "visual": "🍫"},{"text": "Almonds", "visual": "🥜"}],"correct_answer": "Chocolate"}')
        feedback_text = ft.Text("", size=18, weight="bold")
        options_col = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def check_answer(e):
            if e.control.data == quiz_data["correct_answer"]:
                feedback_text.value = "Correct! ✅ +10 Points"
                feedback_text.color = ft.Colors.GREEN
            else:
                feedback_text.value = f"Wrong! ❌ It was {quiz_data['correct_answer']}."
                feedback_text.color = ft.Colors.RED
            for btn in options_col.controls:
                btn.disabled = True
            page.update()

        for opt in quiz_data["options"]:
            options_col.controls.append(
                ft.Button(
                    content=ft.Row([ft.Text(opt["visual"], size=24), ft.Text(opt["text"], size=18)], alignment=ft.MainAxisAlignment.CENTER), 
                    width=280, height=60, data=opt["text"], on_click=check_answer
                )
            )

        page.clean()
        page.add(
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: show_dashboard()),
                ft.Text("GenAI Quiz", size=24, weight="bold")
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=20),
            ft.Text(quiz_data["question"], size=22, weight="bold", text_align="center"),
            ft.Container(height=20),
            options_col,
            ft.Container(height=20),
            feedback_text
        )

    # START THE APP IMMEDIATELY
    show_dashboard()

ft.run(main)