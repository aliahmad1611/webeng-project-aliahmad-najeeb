import flet as ft
import os
from google import genai
from google.genai import types
import asyncio 
import uuid 
from dotenv import load_dotenv
# Import our database manager
from database import db_manager

# --- GEMINI API SETUP ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    chat_config = types.GenerateContentConfig(
        system_instruction="You are a professional avian veterinarian. Provide concise, structured advice. Your name is Pocket Vet AI. Always ask clarifying questions if the user's input is vague. Use bullet points for lists and keep responses under 200 words. Never reveal that you are an AI. Always maintain a friendly and empathetic tone. Dont answer questions that are not related to avian health. If you dont know the answer, say you dont know but suggest possible next steps for the user.",
        temperature=0.7,
    )
except:
    client = None

def create_chat_engine(page: ft.Page):
    db_manager.init_db()

    # --- APP STATE ---
    current_chat_id = None
    sidebar_title_controls = {}

    # --- UI COMPONENTS ---
    chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=20)
    
    message_input = ft.TextField(
        hint_text="Type a message...",
        expand=True,
        border_color=ft.Colors.TRANSPARENT,
        cursor_color=ft.Colors.BLUE_400,
        text_size=16,
        content_padding=15,
    )

    history_list = ft.ListView(expand=True, spacing=5)

    # --- SIDEBAR ACTIONS ---
    def open_sidebar(e):
        sidebar.left = 0 
        page.update()

    def close_sidebar():
        sidebar.left = -250 
        page.update()

    def start_new_chat():
        nonlocal current_chat_id
        current_chat_id = None
        chat_list.controls.clear()
        close_sidebar()
        page.update()

    def load_chat(chat_id):
        nonlocal current_chat_id
        current_chat_id = chat_id
        chat_list.controls.clear()
        
        messages = db_manager.get_chat_messages(chat_id)
        for msg in messages:
            add_message_bubble(msg["role"], msg["text"], update=False)
            
        close_sidebar() 
        page.update()

    def create_sidebar_item(chat_id, title):
        title_control = ft.Text(title, color="white", size=16)
        sidebar_title_controls[chat_id] = title_control 
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color="white", size=18),
                title_control
            ]),
            padding=12,
            border_radius=10,
            ink=True, 
            on_click=lambda e, cid=chat_id: load_chat(cid)
        )

    # --- MESSAGE UI HELPERS ---
    def add_message_bubble(role, text, update=True):
        is_user = role == "user"
        bubble = ft.Container(
            content=ft.Markdown(text, selectable=True, extension_set="github_flavored") if not is_user else ft.Text(text, color="white"),
            padding=12, border_radius=15,
            bgcolor="#22FFFFFF" if not is_user else ft.Colors.BLUE_600, 
            blur=ft.Blur(10, 10, ft.BlurStyle.OUTER) if not is_user else None, 
            alignment=ft.Alignment(-1, -1) if not is_user else ft.Alignment(1, -1),
            expand=True if not is_user else False 
        )
        chat_list.controls.append(ft.Row(controls=[bubble], alignment=ft.MainAxisAlignment.START if not is_user else ft.MainAxisAlignment.END))
        if update: page.update()
        return bubble.content 

    # --- CORE LOGIC ---
    async def process_ai_response(prompt_text, ai_markdown_control, chat_id, is_first_message):
        # 1. Save user message to DB
        db_manager.save_message(chat_id, "user", prompt_text)
        
        # 2. Fetch context and stream AI response
        existing_messages = db_manager.get_chat_messages(chat_id)
        
        try:
            def fetch_stream():
                # ⚡ FIXED: Using the modern, active 2.5-flash model
                temp_session = client.chats.create(model="gemini-2.5-flash", config=chat_config)
                for prev_msg in existing_messages[:-1]:
                    temp_session.send_message(prev_msg["text"])
                return temp_session.send_message_stream(prompt_text)

            response_stream = await asyncio.to_thread(fetch_stream)
            full_response = ""
            ai_markdown_control.value = "" 
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    ai_markdown_control.value = full_response
                    ai_markdown_control.update()
                    await asyncio.sleep(0.01) 
            
            # Save AI message to DB
            db_manager.save_message(chat_id, "model", full_response)
            
            # Generate the title safely AFTER the response finishes streaming
            if is_first_message and client is not None:
                def fetch_title():
                    title_prompt = f"Summarize this into a short 2 to 4 word chat title. No quotes, no punctuation. Text: {prompt_text}"
                    # ⚡ FIXED: Using the modern, active 2.5-flash model
                    return client.models.generate_content(model="gemini-2.5-flash", contents=title_prompt)
                
                try:
                    title_res = await asyncio.to_thread(fetch_title)
                    new_title = title_res.text.strip().replace('"', '')
                    
                    # Update DB and UI
                    db_manager.update_chat_title(chat_id, new_title)
                    if chat_id in sidebar_title_controls:
                        sidebar_title_controls[chat_id].value = new_title
                        sidebar_title_controls[chat_id].update()
                except Exception as title_err:
                    print(f"⚠️ Title Generation Failed: {title_err}")

        except Exception as e:
            ai_markdown_control.value = f"⚠️ Error: {str(e)}"
            ai_markdown_control.update()

    def handle_send(e):
        nonlocal current_chat_id
        if not message_input.value: return
        
        prompt = message_input.value
        message_input.value = ""
        
        # Only create a DB entry if it's the very first message
        is_first_message = False
        if current_chat_id is None:
            current_chat_id = str(uuid.uuid4())
            db_manager.create_chat(current_chat_id, "New Consultation")
            history_list.controls.insert(0, create_sidebar_item(current_chat_id, "New Consultation"))
            is_first_message = True
            page.update()

        # Render UI immediately
        add_message_bubble("user", prompt)
        ai_markdown_control = add_message_bubble("model", "⏳ *Thinking...*")
        
        # Pass the specific chat_id so it saves correctly
        page.run_task(process_ai_response, prompt, ai_markdown_control, current_chat_id, is_first_message)

    # --- DEFINE SIDEBAR ---
    sidebar = ft.Container(
        width=250, left=-250, top=0, bottom=0,  
        bgcolor="#22FFFFFF", blur=ft.Blur(20, 20, ft.BlurStyle.OUTER),
        border=ft.border.only(right=ft.border.BorderSide(1, "#44FFFFFF")),
        padding=20,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=ft.Column([
            ft.Row([
                ft.Text("History", size=22, weight="bold", color="white", expand=True),
                ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=lambda e: close_sidebar())
            ]),
            ft.Divider(color="#55FFFFFF"),
            ft.ElevatedButton("+ New Chat", on_click=lambda e: start_new_chat(), bgcolor=ft.Colors.BLUE_600, color="white", width=210),
            ft.Container(height=10),
            history_list
        ])
    )

    # --- APP STARTUP LOGIC ---
    saved_chats = db_manager.get_all_chats()
    if saved_chats:
        for chat in saved_chats:
            history_list.controls.insert(0, create_sidebar_item(chat["id"], chat["title"]))
        load_chat(saved_chats[-1]["id"])
    else:
        start_new_chat()

    # --- FINAL LAYOUT ---
    return ft.Stack([
        ft.Container(
            expand=True,
            gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#1a1a2e", "#16213e", "#0f3460"])
        ),
        ft.Column([
            ft.Container(
                padding=10,
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.MENU, on_click=open_sidebar, icon_color="white"),
                    ft.Text("Pocket Vet AI", size=20, weight="bold", color="white"),
                ])
            ),
            chat_list,
            ft.Container(
                padding=20,
                content=ft.Container(
                    bgcolor="#11FFFFFF", blur=ft.Blur(20, 20, ft.BlurStyle.OUTER), border_radius=30, border=ft.border.all(1, "#33FFFFFF"), padding=ft.padding.only(left=10, right=10),
                    content=ft.Row([message_input, ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=ft.Colors.BLUE_400, on_click=handle_send)])
                )
            )
        ], expand=True),
        sidebar
    ])