import flet as ft
from google import genai
from google.genai import types
import asyncio
import os
import base64
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
    
    # --- 1. STATE MANAGEMENT (IN-MEMORY) ---
    # We no longer save files to the hard drive. We hold the raw bytes in memory!
    selected_image_bytes = None
    selected_image_mime = "image/jpeg"

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

    # --- 3. THE NEXT-GEN IN-MEMORY FILE PICKER ---
    def on_file_picked(e):
        nonlocal selected_image_bytes, selected_image_mime
        
        # Check if a file was successfully picked
        if e.files and len(e.files) > 0:
            f = e.files[0]
            
            # The actual image bytes are passed directly from the web browser!
            if f.content:
                selected_image_bytes = f.content
                
                # Assign the correct Mime Type for Gemini
                if f.name.lower().endswith(".png"): selected_image_mime = "image/png"
                elif f.name.lower().endswith(".webp"): selected_image_mime = "image/webp"
                else: selected_image_mime = "image/jpeg"
                
                # Convert the bytes to Base64 to display it in the Flet UI
                encoded_string = base64.b64encode(f.content).decode("utf-8")
                
                image_display.content = ft.Image(src_base64=encoded_string, fit="cover", expand=True)
                image_display.border = ft.border.all(2, "#CE82FF") 
                analyze_btn.disabled = False
                result_markdown.value = "*Image loaded securely into memory. Ready for AI Analysis.*"
                page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def trigger_upload(e):
        # ⚡ THE FIX: with_data=True reads the file into memory instantly without saving it!
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "webp"], with_data=True)

    # --- 4. AI ANALYSIS LOGIC ---
    async def process_image_analysis():
        try:
            if client is None:
                raise ValueError("Gemini API Client failed to initialize. Check your API key.")

            if not selected_image_bytes:
                raise ValueError("No image data found in memory.")

            def fetch_vision():
                vision_prompt = """
                You are an expert avian veterinarian and ornithologist. Analyze this image. 
                1. If it's a bird, identify the likely species and mutation/coloration. Check for visible health issues.
                2. If it's a cage, analyze the setup for safety.
                3. If it's droppings, analyze for health indicators.
                Keep your response highly structured, professional, and concise. Use markdown bolding for key terms.
                """
                
                # We feed the raw memory bytes straight to Google GenAI
                return client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(data=selected_image_bytes, mime_type=selected_image_mime),
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
        if not selected_image_bytes: return
        analyze_btn.disabled = True
        loading_indicator.visible = True
        result_markdown.value = "⏳ *Avian Eye is scanning the image...*"
        page.update()
        page.run_task(process_image_analysis)

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
