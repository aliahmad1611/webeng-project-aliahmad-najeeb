import flet as ft
from database import db_manager

def create_onboarding_engine(page: ft.Page, on_complete):
    
    # Data we will collect
    user_data = {
        "bird": None,
        "experience": None,
        "goal": None
    }
    
    current_step = 1
    total_steps = 3

    # UI Components
    progress_bar = ft.ProgressBar(value=0.33, color="#58CC02", bgcolor="#22FFFFFF", height=10, border_radius=5)
    content_area = ft.Container(expand=True)

    def next_step():
        nonlocal current_step
        current_step += 1
        progress_bar.value = current_step / total_steps
        
        if current_step == 2:
            content_area.content = build_experience_screen()
        elif current_step == 3:
            content_area.content = build_goal_screen()
        elif current_step > 3:
            finish_onboarding()
            
        page.update()

    def finish_onboarding():
        session = db_manager.get_active_session()
        if session:
            user_id = session[0]
            # Save data and flag onboarding as complete!
            db_manager.save_onboarding_data(user_id, user_data["bird"], user_data["experience"], user_data["goal"])
        on_complete()

    # --- Screen 1: Choose Bird ---
    def set_bird(e, bird_name):
        user_data["bird"] = bird_name
        next_step()

    def build_bird_screen():
        birds = [("Lovebird", "🐦"), ("Budgie", "🦜"), ("Cockatiel", "🎵"), ("Zebra Finch", "⚡")]
        col = ft.Column(spacing=15)
        for name, emoji in birds:
            btn = ft.ElevatedButton(
                content=ft.Row([ft.Text(emoji, size=24), ft.Text(name, size=16, weight="bold")]),
                style=ft.ButtonStyle(color="white", bgcolor="#11FFFFFF", padding=20, shape=ft.RoundedRectangleBorder(radius=15)),
                on_click=lambda e, b=name: set_bird(e, b)
            )
            col.controls.append(btn)
        return ft.Column([ft.Text("What bird are you caring for?", size=24, weight="bold", color="white"), ft.Container(height=20), col], expand=True)

    # --- Screen 2: Experience ---
    def set_exp(e, exp):
        user_data["experience"] = exp
        next_step()

    def build_experience_screen():
        levels = ["Beginner (Never owned a bird)", "Intermediate (Owned birds before)", "Advanced (Breeder / Expert)"]
        col = ft.Column(spacing=15)
        for lvl in levels:
            btn = ft.ElevatedButton(
                content=ft.Text(lvl, size=16),
                style=ft.ButtonStyle(color="white", bgcolor="#11FFFFFF", padding=20, shape=ft.RoundedRectangleBorder(radius=15)),
                on_click=lambda e, l=lvl: set_exp(e, l)
            )
            col.controls.append(btn)
        return ft.Column([ft.Text("What is your experience level?", size=24, weight="bold", color="white"), ft.Container(height=20), col], expand=True)

    # --- Screen 3: Goal ---
    def set_goal(e, goal):
        user_data["goal"] = goal
        next_step()

    def build_goal_screen():
        goals = ["Taming & Bonding", "Breeding", "General Pet Care"]
        col = ft.Column(spacing=15)
        for g in goals:
            btn = ft.ElevatedButton(
                content=ft.Text(g, size=16),
                style=ft.ButtonStyle(color="white", bgcolor="#11FFFFFF", padding=20, shape=ft.RoundedRectangleBorder(radius=15)),
                on_click=lambda e, g_val=g: set_goal(e, g_val)
            )
            col.controls.append(btn)
        return ft.Column([ft.Text("What is your primary goal?", size=24, weight="bold", color="white"), ft.Container(height=20), col], expand=True)

    # Initialize first screen
    content_area.content = build_bird_screen()

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]),
        padding=20,
        content=ft.Column([
            ft.Container(height=20),
            progress_bar,
            ft.Container(height=30),
            content_area
        ])
    )