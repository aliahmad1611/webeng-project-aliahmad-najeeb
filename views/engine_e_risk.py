import flet as ft
import os
from datetime import datetime
from fpdf import FPDF
from database import db_manager

def create_risk_engine(page: ft.Page):
    main_display = ft.Container(expand=True)

    def refresh_dashboard(e=None):
        session = db_manager.get_active_session()
        user_id = session[0] if session else 1
        user_name = session[1] if session else "Avian Enthusiast"
        
        profile = db_manager.get_user_profile(user_id)
        selected_bird = profile[0] if profile else "Budgie"

        # ⚡ 1. BULLETPROOF LESSON MATH (Ignores orphaned DB rows)
        CORE_COURSES = ["Avian Diet Basics", "Taming & Trust", "Genetics & Mutations", "Danger Zones", "Breeding Basics"]
        saved_course_data = db_manager.get_course_progress(user_id)
        
        total_course_progress = 0.0
        total_lesson_score = 0
        
        for c_title in CORE_COURSES:
            c_data = saved_course_data.get(c_title, {"progress": 0.0, "score": 0})
            if isinstance(c_data, dict):
                total_course_progress += c_data.get("progress", 0.0)
                total_lesson_score += c_data.get("score", 0)
            else:
                total_course_progress += float(c_data)
                
        lesson_percentage = min((total_course_progress / len(CORE_COURSES)) * 100, 100.0)

        # ⚡ 2. BULLETPROOF ROUTINE MATH (Immune to old test clicks)
        SEASONS = ["s1", "s2", "s3", "s4"]
        total_routine_points = 0
        MAX_ROUTINE_POINTS = 1680.0 # 420 points * 4 Seasons
        
        for s_id in SEASONS:
            season_score = 0
            for day in range(1, 8):
                state_key = f"{s_id}_day_{day}"
                tasks = db_manager.get_routine_for_date(user_id, state_key)
                alerts = db_manager.get_alerts_for_date(user_id, state_key)
                
                for t_data in tasks.values():
                    if t_data["done"]:
                        season_score += t_data.get("score", 0)
                        
                for passed in alerts.values():
                    if passed:
                        season_score += 10
            
            # Capping each season to exactly 420 guarantees it matches the Academy Hub perfectly
            total_routine_points += min(season_score, 420)
        
        routine_percentage = min((total_routine_points / MAX_ROUTINE_POINTS) * 100, 100.0)

        # The Final Mastery Formula
        final_score = (lesson_percentage * 0.6) + (routine_percentage * 0.4)
        is_passed = final_score >= 95.0

        # Bird-Specific Color Palettes for the Certificate
        bird_styles = {
            "Budgie": {"hex": "#58CC02", "rgb": (88, 204, 2)},
            "Cockatiel": {"hex": "#FFC800", "rgb": (255, 200, 0)},
            "Lovebird": {"hex": "#FF4B4B", "rgb": (255, 75, 75)},
            "Zebra Finch": {"hex": "#00CCFF", "rgb": (0, 204, 255)}
        }
        b_color = bird_styles.get(selected_bird, bird_styles["Budgie"])

        # --- ADVANCED PDF CERTIFICATE GENERATOR ---
        def generate_pdf_certificate(e):
            try:
                pdf = FPDF(orientation="L", unit="mm", format="A4")
                pdf.add_page()

                pdf.set_line_width(3)
                pdf.set_draw_color(*b_color["rgb"])
                pdf.rect(10, 10, 277, 190)
                pdf.set_line_width(0.5)
                pdf.set_draw_color(26, 26, 46)
                pdf.rect(14, 14, 269, 182)

                pdf.set_fill_color(255, 215, 0)
                pdf.ellipse(230, 140, 35, 35, style="F")
                pdf.set_fill_color(230, 180, 0)
                pdf.ellipse(233, 143, 29, 29, style="F")
                
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(255, 255, 255)
                pdf.text(236, 156, "OFFICIAL")
                pdf.text(236, 161, "MASTERY")

                pdf.set_font("Helvetica", "B", 36)
                pdf.set_text_color(26, 26, 46)
                pdf.ln(25)
                pdf.cell(0, 20, "CERTIFICATE OF EXCELLENCE", align="C", center=True)
                pdf.ln(15)

                pdf.set_font("Helvetica", "I", 16)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, "This honors the dedication and expertise of", align="C", center=True)
                pdf.ln(15)

                pdf.set_font("Helvetica", "B", 42)
                pdf.set_text_color(*b_color["rgb"])
                pdf.cell(0, 20, user_name.upper(), align="C", center=True)
                pdf.ln(20)

                pdf.set_font("Helvetica", "", 14)
                pdf.set_text_color(50, 50, 50)
                body_text = f"For achieving a {final_score:.1f}% Mastery Score in the AvianQuest curriculum.\nThis individual has demonstrated exceptional proficiency in the daily care,\nnutrition, and health analytics of the {selected_bird}."
                pdf.multi_cell(0, 8, body_text, align="C", center=True)
                pdf.ln(35)

                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(26, 26, 46)
                pdf.cell(100, 10, "__________________________", align="C")
                pdf.cell(77, 10, "")
                pdf.cell(100, 10, "__________________________", align="C", center=True)
                pdf.ln(8)
                
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(100, 5, "AvianQuest Intelligence", align="C")
                pdf.cell(77, 5, "")
                pdf.cell(100, 5, "Lead Architect", align="C", center=True)

                try:
                    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                    filepath = os.path.join(desktop, f"AvianQuest_Certificate_{user_name.replace(' ', '_')}.pdf")
                    pdf.output(filepath)
                except Exception:
                    filepath = f"AvianQuest_Certificate_{user_name.replace(' ', '_')}.pdf"
                    pdf.output(filepath)

                snack = ft.SnackBar(content=ft.Text(f"Certificate downloaded to:\n{filepath}", color="white"), bgcolor="#58CC02")
                page.overlay.append(snack)
                snack.open = True
                page.update()

            except Exception as ex:
                snack = ft.SnackBar(content=ft.Text(f"Error generating PDF: {str(ex)}", color="white"), bgcolor="#FF4B4B")
                page.overlay.append(snack)
                snack.open = True
                page.update()

        def build_metric_card(title, percentage, icon, color, subtitle=""):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=24),
                        ft.Column([
                            ft.Text(title, size=16, weight="bold", color="white"),
                            ft.Text(subtitle, size=12, color="white54", italic=True) if subtitle else ft.Container(height=0)
                        ], spacing=2)
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.ProgressBar(value=percentage/100, color=color, bgcolor="#22FFFFFF", expand=True, height=8),
                        ft.Text(f"{percentage:.1f}%", size=14, color="white70", weight="bold")
                    ])
                ], spacing=15),
                bgcolor="#11FFFFFF",
                padding=20,
                border_radius=15,
                border=ft.border.all(1, "#33FFFFFF")
            )

        certificate_preview = ft.Container(
            content=ft.Column([
                ft.Text("CERTIFICATE OF EXCELLENCE", size=18, weight="w900", color="#1A1A2E", text_align="center"),
                ft.Container(height=5),
                ft.Container(
                    content=ft.Icon(ft.Icons.FLUTTER_DASH, size=50, color="white"), 
                    bgcolor=b_color["hex"],
                    width=90, height=90,
                    border_radius=45,
                    alignment=ft.Alignment(0, 0),
                    shadow=ft.BoxShadow(spread_radius=2, blur_radius=15, color=b_color["hex"])
                ),
                ft.Container(height=5),
                ft.Text(user_name.upper(), size=26, weight="w900", color=b_color["hex"], text_align="center"),
                ft.Text(f"Certified {selected_bird} Specialist", size=14, color="#1A1A2E", weight="bold", text_align="center"),
                ft.Text(f"Mastery Score: {final_score:.1f}%", size=12, color="#1A1A2E", italic=True, text_align="center"),
                ft.Container(height=10),
                ft.ElevatedButton(
                    content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, color="white", size=20), ft.Text("Save PDF", weight="bold", color="white")]),
                    style=ft.ButtonStyle(bgcolor="#1A1A2E", shape=ft.RoundedRectangleBorder(radius=8)),
                    width=160, height=45,
                    on_click=generate_pdf_certificate
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white", 
            padding=30,
            border_radius=15,
            border=ft.border.all(4, b_color["hex"]), 
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=30, color="#11FFFFFF"),
            width=350,
            alignment=ft.Alignment(0, 0),
            visible=is_passed 
        )

        locked_message = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK_OUTLINE, color="white38", size=50),
                ft.Text("Certificate Locked", size=20, weight="bold", color="white54"),
                ft.Text(f"You need 95% overall mastery to unlock your official AvianQuest certificate.\n\nCurrent Performance: {int(total_routine_points)} / {int(MAX_ROUTINE_POINTS)} Routine Points.", size=14, color="white38", text_align="center")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#11FFFFFF",
            padding=40,
            border_radius=15,
            border=ft.border.all(1, "#33FFFFFF"),
            width=350,
            visible=not is_passed
        )

        dashboard_layout = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Risk & Certification", size=32, weight="w900", color="white"),
                        ft.Text("Your overall proficiency and readiness analytics.", size=14, color="#00CCFF", weight="bold"),
                    ], expand=True),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH, 
                        icon_color="white", 
                        icon_size=28, 
                        tooltip="Refresh Scores", 
                        on_click=refresh_dashboard 
                    ),
                    ft.Container(content=ft.Icon(ft.Icons.VERIFIED_USER, color="white", size=28), bgcolor="#22FFFFFF", padding=10, border_radius=15)
                ]),
                ft.Container(height=20),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("OVERALL MASTERY", size=14, color="white54", weight="bold"),
                        ft.Text(f"{final_score:.1f}%", size=72, weight="w900", color=b_color["hex"] if is_passed else "white"),
                        ft.Text("Pass Requirement: 95.0%", size=12, color="white38")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.symmetric(vertical=10)
                ),
                
                ft.Container(height=10),
                build_metric_card("Flight School Lessons", lesson_percentage, ft.Icons.SCHOOL, "#CE82FF", subtitle=f"Total Accuracy Score: {total_lesson_score} pts"),
                ft.Container(height=10),
                build_metric_card("Daily Routine Consistency", routine_percentage, ft.Icons.CHECK_BOX, "#58CC02", subtitle=f"Performance Score: {int(total_routine_points)} / {int(MAX_ROUTINE_POINTS)} pts"),
                
                ft.Container(height=30),
                
                ft.Row([certificate_preview, locked_message], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=30)

            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        main_display.content = dashboard_layout
        
        if e:
            page.update()

    refresh_dashboard() 

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]),
        padding=20,
        content=main_display
    )