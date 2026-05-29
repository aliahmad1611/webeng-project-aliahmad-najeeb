import flet as ft
from google import genai
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv

# ⚡ THE FIX: You must actually execute the function to load the variables!
load_dotenv()

# --- GEMINI API SETUP ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except:
    client = None

def create_avian_eye_engine(page: ft.Page):
    
    # --- 1. STATE MANAGEMENT ---
    selected_image_path = None
    upload_dir = "uploads"
    
    # Ensure the uploads directory exists on the server to prevent crash
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # --- 2. UI COMPONENTS ---
    image_display = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.ADD_A_PHOTO, size=50, color="white54"),
            ft.Text("Tap 'Upload Photo' to select an image", color="white54")
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        height=250,
        width=float('inf'),
        bgcolor="#11FFFFFF",
        border_radius=20,
        border=ft.border.all(2, "#33FFFFFF"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE, 
        alignment=ft.Alignment(0, 0) 
    )

    result_markdown = ft.Markdown(
        "Upload a photo of your bird, its cage setup, or its droppings for an instant AI analysis.",
        selectable=True,
        extension_set="github_flavored",
    )

    loading_indicator = ft.ProgressBar(color="#CE82FF", bgcolor="#22FFFFFF", visible=False)
    analyze_btn = ft.ElevatedButton("Analyze Image", icon=ft.Icons.DOCUMENT_SCANNER, bgcolor="#CE82FF", color="#1A1A2E", disabled=True, expand=True)

    # --- 3. THE HYBRID WEB/DESKTOP FILE PICKER (Fixed for Flet 0.81.0) ---
    def on_file_picked(e):
        nonlocal selected_image_path
        if e.files and len(e.files) > 0:
            f = e.files[0]
            
            # SCENARIO A: Local Desktop App (Instant path access)
            if f.path: 
                selected_image_path = f.path
                image_display.content = ft.Image(src=selected_image_path, fit="cover", expand=True)
                image_display.border = ft.border.all(2, "#CE82FF") 
                analyze_btn.disabled = False
                result_markdown.value = "*Image loaded successfully from PC. Ready for AI Analysis.*"
                page.update()
            
            # SCENARIO B: Web App (Requires uploading from Browser to Server)
            else:
                result_markdown.value = f"⏳ *Uploading {f.name} to server...*"
                page.update()
                upload_url = page.get_upload_url(f.name, 60) # Generate 60-second temp link
                file_picker.upload([ft.FilePickerUploadFile(f.name, upload_url=upload_url)])

    def on_file_uploaded(e):
        nonlocal selected_image_path
        if e.progress == 1.0: # 100% Complete
            # Save the new server path so Gemini can read it
            selected_image_path = os.path.join(upload_dir, e.file_name)
            
            # Flet web servers automatically host images in the upload_dir at the root "/"
            image_display.content = ft.Image(src=f"/{e.file_name}", fit="cover", expand=True)
            image_display.border = ft.border.all(2, "#CE82FF") 
            analyze_btn.disabled = False
            result_markdown.value = "*Image successfully transferred to server. Ready for AI Analysis.*"
            page.update()

    # Create the picker and attach it invisibly to the page
    file_picker = ft.FilePicker(on_result=on_file_picked, on_upload=on_file_uploaded)
    page.overlay.append(file_picker)

    def trigger_upload(e):
        # This tells Chrome/Safari/Windows to open its native file menu safely
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "webp"])

    # --- 4. AI ANALYSIS LOGIC ---
    async def process_image_analysis(filepath):
        try:
            if client is None:
                raise ValueError("Gemini API Client failed to initialize. Check your API key.")

            def fetch_vision():
                with open(filepath, "rb") as f:
                    image_bytes = f.read()
                
                mime_type = "image/jpeg"
                if filepath.lower().endswith(".png"): mime_type = "image/png"
                elif filepath.lower().endswith(".webp"): mime_type = "image/webp"

                vision_prompt = """
                You are an expert avian veterinarian and ornithologist. Analyze this image. 
                1. If it's a bird, identify the likely species and mutation/coloration. Check for visible health issues.
                2. If it's a cage, analyze the setup for safety.
                3. If it's droppings, analyze for health indicators.
                Keep your response highly structured, professional, and concise. Use markdown bolding for key terms.
                """
                
                return client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        vision_prompt
                    ]
                )
            
            response = await asyncio.to_thread(fetch_vision)
            result_markdown.value = response.text

        except Exception as e:
            result_markdown.value = f"⚠️ **Analysis Failed:**\n{str(e)}"
        
        finally:
            loading_indicator.visible = False
            analyze_btn.disabled = False
            page.update()

    def handle_analyze_click(e):
        if not selected_image_path: return
        analyze_btn.disabled = True
        loading_indicator.visible = True
        result_markdown.value = "⏳ *Avian Eye is scanning the image...*"
        page.update()
        page.run_task(process_image_analysis, selected_image_path)
    
    # ⚡ Attaching the click event to the button
    analyze_btn.on_click = handle_analyze_click

    # --- 5. FINAL LAYOUT ---
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"]),
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Avian Eye", size=32, weight="w900", color="white"),
                    ft.Text("AI-powered visual health analysis.", size=14, color="#CE82FF", weight="bold"),
                ], expand=True),
                ft.Container(content=ft.Icon(ft.Icons.CAMERA_ALT, color="white", size=28), bgcolor="#22FFFFFF", padding=10, border_radius=15)
            ]),
            ft.Container(height=15),
            
            image_display,
            ft.Container(height=10),
            
            ft.Row([
                ft.ElevatedButton(
                    "Upload Photo", 
                    icon=ft.Icons.UPLOAD_FILE, 
                    bgcolor="#22FFFFFF", 
                    color="white", 
                    expand=True,
                    on_click=trigger_upload 
                ),
                analyze_btn
            ]),
            
            ft.Container(height=15),
            loading_indicator,
            
            ft.Container(
                padding=20, 
                border_radius=20, 
                bgcolor="#11FFFFFF", 
                border=ft.border.all(1, "#33FFFFFF"),
                content=ft.Column([
                    ft.Text("Analysis Report", size=18, weight="bold", color="white"),
                    ft.Divider(color="#33FFFFFF"),
                    result_markdown
                ]) 
            ),
            ft.Container(height=30) 
            
        ], scroll=ft.ScrollMode.AUTO) 
    )
