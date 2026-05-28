import flet as ft
from google import genai
from google.genai import types
import asyncio
import os
import tkinter as tk
from tkinter import filedialog
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

    # --- 3. THE NATIVE OS FILE PICKER HACK ---
    def open_native_picker(e):
        nonlocal selected_image_path
        
        root = tk.Tk()
        root.withdraw() 
        root.attributes('-topmost', True) 
        
        filepath = filedialog.askopenfilename(
            title="Select an Avian Photo",
            filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.webp"), ("All Files", "*.*"))
        )
        root.destroy() 
        
        if filepath:
            selected_image_path = filepath
            
            image_display.content = ft.Image(
                src=selected_image_path,
                fit="cover", 
                expand=True
            )
            image_display.border = ft.border.all(2, "#CE82FF") 
            
            analyze_btn.disabled = False
            result_markdown.value = "*Image loaded successfully. Ready for AI Analysis.*"
            page.update()

    # --- 4. AI ANALYSIS LOGIC ---
    async def process_image_analysis(filepath):
        try:
            # ⚡ THE FIX: Safe error handling if the API Key is completely missing
            if client is None:
                raise ValueError("Gemini API Client failed to initialize. Check your .env file and API key.")

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
                    on_click=open_native_picker 
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