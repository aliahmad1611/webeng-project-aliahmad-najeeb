import flet as ft
from database import db_manager 

def create_lessons_engine(page: ft.Page):
    db_manager.init_db()

    # --- 1. USER & BIRD DATA ---
    session = db_manager.get_active_session()
    user_id = session[0] if session else 1
    profile = db_manager.get_user_profile(user_id)
    selected_bird = profile[0] if profile else "Budgie"

    # --- 2. FETCH COURSE PROGRESS & LOCK STATE ---
    saved_progress = db_manager.get_course_progress(user_id)

    courses = [
        {"title": "Avian Diet Basics", "subtitle": "Seeds, Pellets, and Veggie Chop", "icon": ft.Icons.RESTAURANT, "color": "#58CC02", "progress": saved_progress.get("Avian Diet Basics", 0.0)},
        {"title": "Taming & Trust", "subtitle": "Step-up training and bonding", "icon": ft.Icons.FAVORITE, "color": "#FFC800", "progress": saved_progress.get("Taming & Trust", 0.0)},
        {"title": "Genetics & Mutations", "subtitle": "Understanding color inheritance", "icon": ft.Icons.SCIENCE, "color": "#CE82FF", "progress": saved_progress.get("Genetics & Mutations", 0.0)},
        {"title": "Danger Zones", "subtitle": "Household toxins and hazards", "icon": ft.Icons.WARNING_AMBER_ROUNDED, "color": "#FF4B4B", "progress": saved_progress.get("Danger Zones", 0.0)},
        {"title": "Breeding Basics", "subtitle": "Nest boxes and chick care", "icon": ft.Icons.EGG, "color": "#00CCFF", "progress": saved_progress.get("Breeding Basics", 0.0)}
    ]

    # Evaluate what is unlocked
    for i in range(len(courses)):
        if i == 0:
            courses[i]["unlocked"] = True
        else:
            courses[i]["unlocked"] = courses[i-1]["progress"] >= 1.0

    # --- 3. STATE MANAGEMENT ---
    current_quiz = []
    current_q_index = 0
    score = 0
    active_course_ref = None

    main_display = ft.Container(expand=True)

    def show_error(msg):
        snack = ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor="#FF4B4B")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # --- 4. THE QUIZ RUNNER ENGINE ---
    def load_question():
        q_data = current_quiz[current_q_index]
        options_col = ft.Column(spacing=15)
        has_answered = False
        feedback_text = ft.Text("", size=16, weight="bold")
        
        next_button = ft.ElevatedButton(
            content=ft.Text("Next Question" if current_q_index < len(current_quiz) - 1 else "Finish Lesson", size=16, weight="bold"),
            style=ft.ButtonStyle(bgcolor="#58CC02", color="white", shape=ft.RoundedRectangleBorder(radius=10)),
            width=250, height=50, visible=False,
            on_click=lambda e: next_question()
        )

        def check_answer(e, selected_option, icon_control):
            nonlocal has_answered, score
            if has_answered: return 
            has_answered = True
            
            btn_container = e.control 
            is_correct = selected_option == q_data["answer"]
            
            if is_correct:
                score += 1
                btn_container.bgcolor = "#1A58CC02" 
                btn_container.border = ft.border.all(2, "#58CC02")
                icon_control.icon = ft.Icons.CHECK_CIRCLE
                icon_control.color = "#58CC02"
                feedback_text.value = "Correct! Great job."
                feedback_text.color = "#58CC02"
            else:
                btn_container.bgcolor = "#1AFF4B4B" 
                btn_container.border = ft.border.all(2, "#FF4B4B")
                icon_control.icon = ft.Icons.CANCEL
                icon_control.color = "#FF4B4B"
                feedback_text.value = f"Incorrect. The right answer is: {q_data['answer']}"
                feedback_text.color = "#FF4B4B"
                
            next_button.visible = True
            page.update()

        for opt in q_data["options"]:
            opt_icon = ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color="white54")
            opt_container = ft.Container(
                content=ft.Row([opt_icon, ft.Text(opt, size=16, color="white", expand=True)]),
                padding=15, border_radius=15, bgcolor="#11FFFFFF", border=ft.border.all(1, "#33FFFFFF"),
                ink=True,
                on_click=lambda e, o=opt, i=opt_icon: check_answer(e, o, i) 
            )
            options_col.controls.append(opt_container)

        quiz_layout = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.CLOSE, icon_color="white54", on_click=lambda e: show_course_list()),
                    ft.ProgressBar(value=(current_q_index) / len(current_quiz), color="#FFC800", bgcolor="#22FFFFFF", expand=True),
                    ft.Text(f"{current_q_index + 1}/{len(current_quiz)}", color="white54", weight="bold")
                ]),
                ft.Container(height=20),
                ft.Text(f"Target: {selected_bird}", size=12, color="#CE82FF", weight="bold"),
                ft.Text(q_data["question"], size=22, weight="bold", color="white"),
                ft.Container(height=30),
                options_col,
                ft.Container(height=20), 
                ft.Column([feedback_text, next_button], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=20) 
            ], scroll=ft.ScrollMode.AUTO) 
        )
        main_display.content = quiz_layout
        page.update()

    def next_question():
        nonlocal current_q_index
        current_q_index += 1
        if current_q_index < len(current_quiz):
            load_question()
        else:
            finish_quiz()

    def finish_quiz():
        active_course_ref["progress"] = 1.0
        active_course_ref["unlocked"] = True
        
        db_manager.update_course_progress(user_id, active_course_ref["title"], 1.0)
        
        for i in range(len(courses)):
            if courses[i]["title"] == active_course_ref["title"] and i + 1 < len(courses):
                courses[i + 1]["unlocked"] = True
        
        summary = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Container(height=50),
                ft.Icon(ft.Icons.EMOJI_EVENTS, color="#FFC800", size=100),
                ft.Text("Lesson Complete!", size=28, weight="bold", color="white"),
                ft.Text(f"You scored {score} out of {len(current_quiz)}.", size=18, color="white70"),
                ft.Container(height=50),
                ft.ElevatedButton(
                    content=ft.Text("Return to Flight School", size=16, weight="bold"), 
                    style=ft.ButtonStyle(bgcolor="#FFC800", color="#1A1A2E", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=250, height=50, 
                    on_click=lambda e: show_course_list()
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO) 
        )
        main_display.content = summary
        page.update()

    # --- 5. THE COURSE LIST VIEW (GRID STYLE) ---
    def start_lesson(course):
        nonlocal current_quiz, current_q_index, score, active_course_ref
        title = course["title"]
        
        questions = db_manager.get_quiz_questions(selected_bird, title)
        
        if not questions:
            show_error(f"Modules for '{title}' are coming soon!")
            return
            
        active_course_ref = course
        current_quiz = questions
        current_q_index = 0
        score = 0
        load_question()

    def show_course_list():
        grid_row = ft.Row(
            wrap=True,
            spacing=25,
            run_spacing=30,
            alignment=ft.MainAxisAlignment.CENTER
        )

        for course in courses:
            is_completed = course["progress"] >= 1.0
            is_unlocked = course["unlocked"]
            is_active = is_unlocked and not is_completed

            if not is_unlocked:
                bg_color = "#33334A"
                edge_color = "#1A1A2E" 
                ic_color = "white38"
                display_icon = ft.Icons.LOCK
            elif is_completed:
                bg_color = "#FFD900" 
                edge_color = "#D49A00" 
                ic_color = "white"
                display_icon = ft.Icons.STAR_ROUNDED 
            else:
                bg_color = course["color"] 
                edge_color = "black38" 
                ic_color = "white"
                display_icon = course["icon"]

            node_btn = ft.Container(
                content=ft.Icon(display_icon, color=ic_color, size=40),
                width=85, height=85,
                bgcolor=bg_color,
                border_radius=45,
                alignment=ft.Alignment(0, 0), 
                shadow=[
                    ft.BoxShadow(spread_radius=0, blur_radius=0, color=edge_color, offset=ft.Offset(0, 6)),
                    ft.BoxShadow(spread_radius=2, blur_radius=15, color=bg_color) if is_active else ft.BoxShadow(color="transparent")
                ],
                ink=is_unlocked,
                on_click=lambda e, c=course, unl=is_unlocked: start_lesson(c) if unl else show_error("🔒 Complete previous lessons to unlock this!")
            )

            node_wrapper = ft.Container(
                content=ft.Column([
                    node_btn,
                    ft.Container(height=4), 
                    ft.Container(
                        content=ft.Text(course["title"], size=13, weight="w900", color="white" if is_unlocked else "white38", text_align="center", max_lines=2),
                        bgcolor="#22FFFFFF" if is_unlocked else "#0AFFFFFF",
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        border_radius=15,
                        alignment=ft.Alignment(0, 0) # ⚡ FIXED: Replaced `ft.alignment.center` with Flet V1 safe coordinates!
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                width=140, 
                padding=ft.padding.symmetric(vertical=10)
            )
            
            grid_row.controls.append(node_wrapper)

        menu_layout = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Flight School", size=32, weight="w900", color="white"),
                        ft.Text(f"Curriculum customized for your {selected_bird}.", size=14, color="#FFC800", weight="bold"),
                    ], expand=True),
                    ft.Container(content=ft.Icon(ft.Icons.SCHOOL, color="white", size=28), bgcolor="#22FFFFFF", padding=10, border_radius=15)
                ]),
                ft.Container(height=25),
                
                ft.Column([grid_row], scroll=ft.ScrollMode.AUTO, expand=True)
            ])
        )
        main_display.content = menu_layout
        page.update()

    # --- 6. INITIALIZATION ---
    show_course_list()

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]),
        padding=20,
        content=main_display
    )