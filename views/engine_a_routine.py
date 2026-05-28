import flet as ft
from database import db_manager 

def create_routine_engine(page: ft.Page):
    db_manager.init_db()

    session = db_manager.get_active_session()
    user_id = session[0] if session else 1
    profile = db_manager.get_user_profile(user_id)
    selected_bird = profile[0] if profile else "Budgie"
    unlocked_day = profile[1] if profile else 1 

    SEASONS = [
        {"id": "s1", "title": "Summer (High Heat)", "icon": ft.Icons.WB_SUNNY},
        {"id": "s2", "title": "Breeding Season", "icon": ft.Icons.EGG},
        {"id": "s3", "title": "Winter (Cold Drafts)", "icon": ft.Icons.AC_UNIT},
        {"id": "s4", "title": "Spring (Molting)", "icon": ft.Icons.ECO}
    ]

    SEASON_TASKS = {
        "s1": [
            {"title": "Morning Water Change", "icon": ft.Icons.WATER_DROP},
            {"title": "Provide Seed Mix", "icon": ft.Icons.SET_MEAL},
            {"title": "Provide Soft Food / Chop", "icon": ft.Icons.RESTAURANT},
            {"title": "Evening Water Change", "icon": ft.Icons.NIGHTLIGHT_ROUND}
        ],
        "s2": [
            {"title": "Check Nest Box", "icon": ft.Icons.HOME},
            {"title": "Add Calcium Supplement", "icon": ft.Icons.EGG},
            {"title": "Provide High-Protein Egg Food", "icon": ft.Icons.RESTAURANT},
            {"title": "Evening Water Change", "icon": ft.Icons.NIGHTLIGHT_ROUND}
        ],
        "s3": [
            {"title": "Check Window Drafts", "icon": ft.Icons.WIND_POWER},
            {"title": "Provide High-Fat Seed Mix", "icon": ft.Icons.SET_MEAL},
            {"title": "Provide Warm Water", "icon": ft.Icons.WATER_DROP},
            {"title": "Cover Cage for Evening", "icon": ft.Icons.NIGHTLIGHT_ROUND}
        ],
        "s4": [
            {"title": "Provide Bathing Dish", "icon": ft.Icons.BATHROOM},
            {"title": "Provide Seed & Vitamin Mix", "icon": ft.Icons.SET_MEAL},
            {"title": "Vacuum Molted Feathers", "icon": ft.Icons.CLEANING_SERVICES},
            {"title": "Evening Water Change", "icon": ft.Icons.NIGHTLIGHT_ROUND}
        ]
    }

    main_layout = ft.Container(expand=True)
    
    def show_error(msg):
        snack = ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor="#FF4B4B")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def get_season_progress():
        progress_data = {}
        is_next_unlocked = True 
        
        for s in SEASONS:
            s_id = s["id"]
            completed_items = 0
            total_score = 0
            total_possible_items = 42 
            max_season_score = 420.0 # ⚡ The ultimate score ceiling
            
            for day in range(1, 8):
                state_key = f"{s_id}_day_{day}"
                tasks = db_manager.get_routine_for_date(user_id, state_key)
                alerts = db_manager.get_alerts_for_date(user_id, state_key)
                
                for t_data in tasks.values():
                    if t_data["done"]:
                        completed_items += 1
                        total_score += t_data.get("score", 0)
                        
                for passed in alerts.values():
                    if passed:
                        completed_items += 1
                        total_score += 10 
            
            # ⚡ STRICT MATH FIX: Percentage is now tied explicitly to the score and clamped at 1.0 (100%)
            clamped_score = min(total_score, int(max_season_score))
            prog_val = clamped_score / max_season_score
            
            progress_data[s_id] = {
                "progress": prog_val, 
                "score": clamped_score, 
                "unlocked": is_next_unlocked
            }
            # Forgive a few missed testing clicks to ensure the next season unlocks
            is_next_unlocked = (completed_items >= (total_possible_items - 5))
            
        return progress_data

    def build_hub_view():
        progress_data = get_season_progress()
        cards = []
        for s in SEASONS:
            s_id = s["id"]
            is_unlocked = progress_data[s_id]["unlocked"]
            prog_val = progress_data[s_id]["progress"]
            score = progress_data[s_id]["score"]
            
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(s["icon"], color="#CE82FF" if is_unlocked else "white24", size=30),
                        ft.Text(s["title"], size=18, weight="bold", color="white" if is_unlocked else "white38", expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT if is_unlocked else ft.Icons.LOCK, color="white" if is_unlocked else "white38")
                    ]),
                    ft.Container(height=10),
                    ft.Column([
                        ft.Row([
                            ft.Text("Season Completion", size=12, color="white54"), 
                            ft.Text(f"⭐ {score} / 420 pts  •  {int(prog_val * 100)}%", size=12, color="white" if is_unlocked else "white54", weight="bold")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=prog_val, color="#58CC02", bgcolor="#22FFFFFF", height=6)
                    ], spacing=5)
                ]),
                padding=20, bgcolor="#11FFFFFF" if is_unlocked else "#0AFFFFFF", border_radius=15, border=ft.border.all(1, "#33FFFFFF") if is_unlocked else ft.border.all(1, "#11FFFFFF"),
                ink=is_unlocked,
                on_click=lambda e, unl=is_unlocked, tit=s["title"], sid=s["id"]: open_season(tit, sid) if unl else show_error("🔒 Complete previous season to unlock.")
            )
            cards.append(card)
            
        return ft.Column([
            ft.Text("Academy Hub", size=32, weight="w900", color="white"),
            ft.Text("Master your flock one season at a time.", size=14, color="#CE82FF", weight="bold"),
            ft.Container(height=20),
            ft.Column(cards, spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True)

    def open_season(season_title, season_id):
        nonlocal unlocked_day
        profile = db_manager.get_user_profile(user_id)
        unlocked_day = profile[1] if profile else 1 

        active_day = unlocked_day 
        day_buttons_row = ft.Row(scroll=ft.ScrollMode.AUTO)
        content_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=20)
        
        active_tasks = SEASON_TASKS.get(season_id, SEASON_TASKS["s1"])
        
        def render_day_content():
            content_col.controls.clear()
            state_key = f"{season_id}_day_{active_day}"
            
            saved_tasks = db_manager.get_routine_for_date(user_id, state_key)
            saved_alerts = db_manager.get_alerts_for_date(user_id, state_key)

            # 1. DAILY STRICT ROUTINE
            task_cards = []
            for t in active_tasks:
                task_data = saved_tasks.get(t["title"], {"done": False, "time": None, "score": 0})
                is_done = task_data["done"]
                time_str = task_data["time"]
                score = task_data["score"]
                
                display_text = f"{time_str}  •  ⭐ {score}/10" if is_done else "Pending"
                
                check_icon = ft.Icon(ft.Icons.CHECK_CIRCLE if is_done else ft.Icons.RADIO_BUTTON_UNCHECKED, color="#58CC02" if is_done else "white54")
                time_label = ft.Text(display_text, size=12, color="#58CC02" if is_done else "white38", weight="bold")
                
                def on_task_click(e, t_title=t["title"], icon=check_icon, lbl=time_label):
                    new_state = icon.icon == ft.Icons.RADIO_BUTTON_UNCHECKED
                    timestamp, updated_score = db_manager.update_routine_task(user_id, state_key, t_title, new_state)
                    
                    icon.icon = ft.Icons.CHECK_CIRCLE if new_state else ft.Icons.RADIO_BUTTON_UNCHECKED
                    icon.color = "#58CC02" if new_state else "white54"
                    lbl.value = f"{timestamp}  •  ⭐ {updated_score}/10" if new_state else "Pending"
                    lbl.color = "#58CC02" if new_state else "white38"
                    page.update()

                card = ft.Container(
                    content=ft.Row([
                        ft.Icon(t["icon"], color="white70"),
                        ft.Column([ft.Text(t["title"], weight="bold", color="white"), time_label], expand=True, spacing=2),
                        check_icon
                    ]),
                    padding=15, bgcolor="#11FFFFFF", border_radius=10, ink=True, on_click=on_task_click
                )
                task_cards.append(card)

            content_col.controls.append(ft.Text(f"Strict Routine ({selected_bird})", size=18, weight="bold", color="white"))
            content_col.controls.extend(task_cards)

            # 2. EMERGENCY ALERTS
            content_col.controls.append(ft.Container(height=10))
            content_col.controls.append(ft.Text(f"Daily Alerts (Day {active_day})", size=18, weight="bold", color="#FF4B4B"))
            
            daily_db_alerts = db_manager.get_daily_alerts(selected_bird, season_title, active_day)
            
            if not daily_db_alerts:
                content_col.controls.append(ft.Text("No specific alerts for today. Enjoy the peace!", color="white54", italic=True))

            for al in daily_db_alerts:
                db_id = al["db_id"]
                is_passed = saved_alerts.get(db_id, False)
                
                icon_choice = ft.Icons.LOCAL_HOSPITAL if al["type"] == "Disease" else ft.Icons.WARNING
                badge_text = "Disease Alert" if al["type"] == "Disease" else "Emergency"
                
                def answer_alert(e, option, correct_ans, alert_id, dialog_ref):
                    if option == correct_ans:
                        db_manager.update_alert_status(user_id, state_key, alert_id, True)
                        dialog_ref.open = False
                        render_day_content() 
                    else:
                        e.control.style = ft.ButtonStyle(bgcolor="#FF4B4B", color="white")
                        e.control.content = ft.Text("Wrong Action! Try again.")
                        page.update()

                def open_alert_dialog(e, alert_data):
                    options_col = ft.Column()
                    dialog = ft.AlertDialog(title=ft.Text(f"{alert_data['title']}", color="#FF4B4B", weight="bold"), content=ft.Column([ft.Text(alert_data['desc'], color="white"), ft.Container(height=10), options_col], tight=True), bgcolor="#1A1A2E")
                    for opt in alert_data['options']:
                        btn = ft.ElevatedButton(content=ft.Text(opt), style=ft.ButtonStyle(bgcolor="#33FFFFFF", color="white"), on_click=lambda e, o=opt, a=alert_data['ans'], aid=alert_data['db_id'], d=dialog: answer_alert(e, o, a, aid, d))
                        options_col.controls.append(btn)
                    page.overlay.append(dialog)
                    dialog.open = True
                    page.update()

                al_card = ft.Container(
                    content=ft.Row([
                        ft.Icon(icon_choice if not is_passed else ft.Icons.GPP_GOOD, color="white" if not is_passed else "#58CC02"),
                        ft.Column([
                            ft.Text(al["title"], weight="bold", color="white" if not is_passed else "white54"), 
                            ft.Text(f"Passed (+10 pts)" if is_passed else badge_text, size=12, color="#58CC02" if is_passed else "white70")
                        ], expand=True)
                    ]),
                    padding=15, bgcolor="#11FFFFFF" if is_passed else "#FF4B4B", border_radius=10, ink=not is_passed,
                    border=ft.border.all(1, "#58CC02") if is_passed else None,
                    on_click=lambda e, data=al: open_alert_dialog(e, data) if not saved_alerts.get(data["db_id"], False) else None
                )
                content_col.controls.append(al_card)
                
            if active_day == unlocked_day and active_day < 7:
                content_col.controls.append(ft.Container(height=20))
                content_col.controls.append(
                    ft.ElevatedButton("Fast Forward to Next Day", icon=ft.Icons.FAST_FORWARD, bgcolor="#CE82FF", color="#1A1A2E", height=50, width=float('inf'),
                        on_click=lambda e: simulate_next_day()
                    )
                )
            page.update()

        def simulate_next_day():
            nonlocal unlocked_day, active_day
            db_manager.unlock_next_day(user_id)
            unlocked_day += 1
            active_day = unlocked_day
            build_day_tabs()
            render_day_content()

        def build_day_tabs():
            day_buttons_row.controls.clear()
            for i in range(1, 8):
                is_locked = i > unlocked_day
                btn = ft.ElevatedButton(
                    content=ft.Row([ft.Icon(ft.Icons.LOCK, size=14) if is_locked else ft.Container(), ft.Text(f"Day {i}")]),
                    style=ft.ButtonStyle(
                        color="#1A1A2E" if i == active_day else "white38" if is_locked else "white",
                        bgcolor="#CE82FF" if i == active_day else "#0AFFFFFF" if is_locked else "#22FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda e, day_num=i, l=is_locked: (set_active_day(day_num) if not l else show_error("🔒 Wait until tomorrow to unlock this day."))
                )
                day_buttons_row.controls.append(btn)
            page.update()

        def set_active_day(day_num):
            nonlocal active_day
            active_day = day_num
            build_day_tabs()
            render_day_content()

        build_day_tabs()
        render_day_content()

        main_layout.content = ft.Column([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: (setattr(main_layout, 'content', build_hub_view()), page.update())),
            ft.Text(season_title, size=28, weight="w900", color="white"),
            day_buttons_row,
            ft.Container(height=10),
            content_col
        ], expand=True)
        page.update()

    main_layout.content = build_hub_view()

    return ft.Container(expand=True, gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]), padding=20, content=main_layout)