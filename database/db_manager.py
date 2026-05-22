import sqlite3
import os
import json
import bcrypt
from datetime import datetime 

DB_PATH = os.path.join(os.path.dirname(__file__), "avianquest.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Secure Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    columns_to_add_users = [
        "selected_bird TEXT",
        "knowledge_level TEXT",
        "experience TEXT",
        "goal TEXT",
        "onboarding_completed INTEGER DEFAULT 0",
        "current_season_day INTEGER DEFAULT 1" 
    ]
    
    for col in columns_to_add_users:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass 

    # Local Session Table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_session (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            user_id INTEGER,
            name TEXT
        )
    """)

    # Chat Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            text_content TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )
    """)

    # Routine Tracker Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routine_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT,
            title TEXT,
            completed INTEGER,
            user_id INTEGER,
            state_key TEXT,
            completed_time TEXT,
            score INTEGER DEFAULT 0
        )
    """)
    
    columns_to_add_routine = [
        "user_id INTEGER",
        "state_key TEXT",
        "completed_time TEXT",
        "score INTEGER DEFAULT 0" 
    ]
    for col in columns_to_add_routine:
        try:
            cursor.execute(f"ALTER TABLE routine_tasks ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass

    # Emergency Alerts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            state_key TEXT,
            alert_id TEXT,
            passed INTEGER
        )
    """)

    # GLOBAL ALERT BANK 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bird_type TEXT, 
            season TEXT, 
            day_number INTEGER,
            alert_type TEXT, 
            title TEXT, 
            description TEXT, 
            options TEXT, 
            answer TEXT
        )
    """)

    # Seed the MASSIVE 224-alert curriculum
    cursor.execute("SELECT COUNT(*) FROM alert_bank")
    if cursor.fetchone()[0] < 200:
        cursor.execute("DELETE FROM alert_bank")
        
        birds = ["Lovebird", "Budgie", "Cockatiel", "Zebra Finch"]
        
        # --- SUMMER DATA ---
        summer_em = [
            ("Heat Stroke", "Your {bird} is panting heavily and holding wings away from its body in the 40°C heat.", ["Mist with water & move to shade", "Cover cage", "Feed seeds"], "Mist with water & move to shade"),
            ("Water Spoilage", "The water tube is green with algae from the summer sun.", ["Scrub with vinegar/water", "Leave it", "Add bleach"], "Scrub with vinegar/water"),
            ("Night Frights", "Your {bird} is thrashing in the dark due to a summer thunderstorm.", ["Turn on a dim nightlight", "Yell at it", "Cover with thick blanket"], "Turn on a dim nightlight"),
            ("Blood Feather", "A new feather broke and is bleeding profusely.", ["Apply styptic powder & hold pressure", "Pull it with pliers", "Wait"], "Apply styptic powder & hold pressure"),
            ("Ant Invasion", "Ants are swarming the fresh food bowl.", ["Use bird-safe diatomaceous earth", "Spray bug spray", "Ignore"], "Use bird-safe diatomaceous earth"),
            ("Dehydration", "Sunken eyes and lethargy in high heat.", ["Offer pedialyte/water via syringe", "Give dry crackers", "Put in sun"], "Offer pedialyte/water via syringe"),
            ("Stuck Molt", "Pin feathers are hard and uncomfortable in dry heat.", ["Provide a shallow bath", "Pull them out", "Lower humidity"], "Provide a shallow bath")
        ]
        summer_dis = [
            ("Sour Crop (Bacterial)", "The soft food spoiled in the heat. Your {bird} is vomiting.", ["Remove food & call Avian Vet", "Feed more", "Give human antibiotics"], "Remove food & call Avian Vet"),
            ("Scaly Face Mites", "Crusty lesions appearing on the beak and legs.", ["Apply Ivermectin via Vet", "Scrub with soap", "Do nothing"], "Apply Ivermectin via Vet"),
            ("Aspergillosis (Fungal)", "Wheezing and tail-bobbing. Mold grew in damp cage corners.", ["Vet visit for antifungals", "Give a bath", "Cover the cage"], "Vet visit for antifungals"),
            ("Bumblefoot", "Red, swollen lesions on the bottom of the feet from hard perches.", ["Wrap perches in vet tape & consult vet", "Pop the blister", "Provide sandpaper perches"], "Wrap perches in vet tape & consult vet"),
            ("Respiratory Infection", "Sneezing and nasal discharge after being near a cold AC draft.", ["Move away from AC & keep warm", "Put in front of fan", "Spray with water"], "Move away from AC & keep warm"),
            ("Avian Gastric Yeast", "Weight loss despite eating constantly.", ["Vet visit & specialized medication", "Feed only seeds", "Wait a week"], "Vet visit & specialized medication"),
            ("Psittacosis", "Lime green droppings and lethargy.", ["Isolate immediately & rush to Vet", "Put with other birds", "Give vitamins"], "Isolate immediately & rush to Vet")
        ]

        # --- BREEDING DATA ---
        breed_em = [
            ("Egg Binding", "Female {bird} straining at bottom of cage.", ["Apply warmth/humidity & rush to vet", "Squeeze egg out", "Give cold bath"], "Apply warmth/humidity & rush to vet"),
            ("Territorial Aggression", "Male is attacking your hands near nest.", ["Use target training away from cage", "Hit beak", "Wear thick gloves permanently"], "Use target training away from cage"),
            ("Nesting Ingestion", "Eating cotton nesting fibers causing blockage.", ["Remove cotton, use paper/wood shavings", "Give more cotton", "Do nothing"], "Remove cotton, use paper/wood shavings"),
            ("Calcium Crash", "Female is twitching and has soft-shelled eggs.", ["Liquid calcium supplement immediately", "Give more seeds", "Remove nest box"], "Liquid calcium supplement immediately"),
            ("Splayed Legs", "Chicks' legs are pointing outward.", ["Vet to apply sponge hobbles", "Snap them back", "Ignore it"], "Vet to apply sponge hobbles"),
            ("Mate Aggression", "Male attacking female.", ["Separate them immediately", "Let them fight", "Spray with water"], "Separate them immediately"),
            ("Chick Abandonment", "Parents stopped feeding the chick.", ["Hand-feed with formula & brooder", "Force parents to feed", "Give chick solid seeds"], "Hand-feed with formula & brooder")
        ]
        breed_dis = [
            ("Egg Yolk Peritonitis", "Swollen abdomen, fluid buildup.", ["Emergency Vet surgery/antibiotics", "Pop the swelling", "Give vitamins"], "Emergency Vet surgery/antibiotics"),
            ("Cloacal Prolapse", "Pink tissue protruding from vent.", ["Keep moist & Emergency Vet", "Push it back in", "Apply alcohol"], "Keep moist & Emergency Vet"),
            ("Sour Crop (Chicks)", "Formula not emptying from chick's crop.", ["Flush crop via Vet, check brooder temp", "Feed more formula", "Squeeze crop"], "Flush crop via Vet, check brooder temp"),
            ("Polyomavirus", "Chicks have swollen bellies and bruising.", ["Biosecurity & Vet support", "Change seed brand", "Give bath"], "Biosecurity & Vet support"),
            ("Trichomoniasis", "White plaques in the throat.", ["Vet prescribed Ronidazole", "Scrape plaques off", "Give apple cider vinegar"], "Vet prescribed Ronidazole"),
            ("PBFD", "Chicks growing deformed feathers.", ["Isolate & test via bloodwork", "Pull feathers out", "Give more sunlight"], "Isolate & test via bloodwork"),
            ("Candidiasis", "White fungal growth in the mouth.", ["Antifungal (Nystatin) via Vet", "Scrub mouth", "Give bread"], "Antifungal (Nystatin) via Vet")
        ]

        # --- WINTER DATA ---
        winter_em = [
            ("Hypothermia", "Your {bird} is fluffed up and shivering.", ["Provide safe reptile heat lamp/pad", "Put in oven", "Force to fly"], "Provide safe reptile heat lamp/pad"),
            ("Teflon Toxicity", "Used non-stick pan/space heater. Bird gasping.", ["Ventilate room & rush to Vet", "Cover cage", "Give CPR"], "Ventilate room & rush to Vet"),
            ("Dry Air / Skin", "Bird constantly scratching due to indoor heating.", ["Use a cool-mist humidifier", "Apply lotion", "Stop bathing"], "Use a cool-mist humidifier"),
            ("Thermal Burn", "Bird sat directly on unprotected heat lamp.", ["Cool water compress & Vet", "Apply butter", "Pop blister"], "Cool water compress & Vet"),
            ("Vitamin D Deficiency", "Lethargy due to lack of winter sunlight.", ["Provide full-spectrum avian UVB light", "Give human D3 pills", "Put outside in cold"], "Provide full-spectrum avian UVB light"),
            ("Draft Exposure", "Cold wind leaking from window.", ["Seal window & cover half of cage", "Turn fan on", "Give hot tea"], "Seal window & cover half of cage"),
            ("Frostbite", "Toes turning black/blue.", ["Warm slowly & Emergency Vet", "Rub vigorously", "Apply ice"], "Warm slowly & Emergency Vet")
        ]
        winter_dis = [
            ("Upper Respiratory", "Clicking breathing and nasal discharge.", ["Vet visit & keep warm", "Wipe nose with tissue", "Give cold bath"], "Vet visit & keep warm"),
            ("Pneumonia", "Tail bobbing and open-mouth breathing.", ["Oxygen therapy via Vet", "Put in bathroom", "Give CPR"], "Oxygen therapy via Vet"),
            ("Aspergillosis", "Winter closed windows caused mold growth.", ["Antifungal meds via Vet", "Open all windows wide", "Ignore"], "Antifungal meds via Vet"),
            ("Sinusitis", "Swelling around eyes.", ["Flush sinuses via Vet", "Squeeze swelling", "Apply human eye drops"], "Flush sinuses via Vet"),
            ("Scaly Leg Mites", "Crust spreading in dry conditions.", ["Ivermectin treatment", "Apply olive oil", "Scrub scales"], "Ivermectin treatment"),
            ("Arthritic Flare-up", "Limping on cold mornings.", ["Flat perches & Vet pain meds", "Force exercise", "Massage aggressively"], "Flat perches & Vet pain meds"),
            ("Conjunctivitis", "Red, weeping eyes.", ["Antibiotic eye drops via Vet", "Wash with tap water", "Leave it"], "Antibiotic eye drops via Vet")
        ]

        # --- SPRING DATA ---
        spring_em = [
            ("Stuck Molt", "Painful pin feathers covering the head.", ["Mist daily to soften sheaths", "Pluck them out", "Brush with comb"], "Mist daily to soften sheaths"),
            ("Blood Feather Break", "Bleeding from a newly growing flight feather.", ["Styptic powder & pressure", "Wash with water", "Wait"], "Styptic powder & pressure"),
            ("Hormonal Frustration", "Rubbing on toys, aggressive biting.", ["Ensure 12 hrs sleep & remove mirrors", "Yell at bird", "Give a nest box"], "Ensure 12 hrs sleep & remove mirrors"),
            ("Over-Preening", "Chewing feathers to the shaft.", ["Provide foraging toys & vet check", "Spray with bitter apple", "Put a cone on"], "Provide foraging toys & vet check"),
            ("Vitamin A Deficiency", "Dull feathers post-molt.", ["Feed red/orange veggies (carrots/sweet potato)", "Give more seeds", "Give meat"], "Feed red/orange veggies (carrots/sweet potato)"),
            ("Window Collision", "Flew into glass due to spring energy.", ["Dark, quiet box & Vet exam", "Force to fly again", "Apply ice to head"], "Dark, quiet box & Vet exam"),
            ("Heavy Molt Exhaustion", "Sleeping more than usual, grumpy.", ["Increase protein (egg food)", "Force them to play", "Reduce food"], "Increase protein (egg food)")
        ]
        spring_dis = [
            ("Feather Cysts", "Lump under skin where feather failed to grow.", ["Vet surgical removal", "Pop with needle", "Squeeze it"], "Vet surgical removal"),
            ("Bacterial Dermatitis", "Skin infection from excessive scratching.", ["Antibiotics & collar via Vet", "Apply human Neosporin", "Give bath"], "Antibiotics & collar via Vet"),
            ("Giardia", "Foul-smelling diarrhea and feather plucking.", ["Vet stool test & Metronidazole", "Change water", "Give crackers"], "Vet stool test & Metronidazole"),
            ("Psittacosis", "Springtime lethargy and green urates.", ["Doxycycline treatment via Vet", "Isolate only", "Change diet"], "Doxycycline treatment via Vet"),
            ("Pacheco's Disease", "Sudden weakness and yellow urates.", ["Supportive care & Vet", "Give vitamins", "Keep warm only"], "Supportive care & Vet"),
            ("Fungal Skin Infection", "Red, itchy patches.", ["Topical antifungals via Vet", "Apply rubbing alcohol", "Ignore"], "Topical antifungals via Vet"),
            ("Bumblefoot", "Sores from heavy spring pacing.", ["Soft perches & Vet wrap", "Pop the sore", "Use sandpaper covers"], "Soft perches & Vet wrap")
        ]

        alert_seed = []
        for bird in birds:
            for day in range(1, 8):
                idx = day - 1 
                # Summer
                alert_seed.append((bird, "Summer (High Heat)", day, "Emergency", summer_em[idx][0], summer_em[idx][1].replace("{bird}", bird), json.dumps(summer_em[idx][2]), summer_em[idx][3]))
                alert_seed.append((bird, "Summer (High Heat)", day, "Disease", summer_dis[idx][0], summer_dis[idx][1].replace("{bird}", bird), json.dumps(summer_dis[idx][2]), summer_dis[idx][3]))
                # Breeding
                alert_seed.append((bird, "Breeding Season", day, "Emergency", breed_em[idx][0], breed_em[idx][1].replace("{bird}", bird), json.dumps(breed_em[idx][2]), breed_em[idx][3]))
                alert_seed.append((bird, "Breeding Season", day, "Disease", breed_dis[idx][0], breed_dis[idx][1].replace("{bird}", bird), json.dumps(breed_dis[idx][2]), breed_dis[idx][3]))
                # Winter
                alert_seed.append((bird, "Winter (Cold Drafts)", day, "Emergency", winter_em[idx][0], winter_em[idx][1].replace("{bird}", bird), json.dumps(winter_em[idx][2]), winter_em[idx][3]))
                alert_seed.append((bird, "Winter (Cold Drafts)", day, "Disease", winter_dis[idx][0], winter_dis[idx][1].replace("{bird}", bird), json.dumps(winter_dis[idx][2]), winter_dis[idx][3]))
                # Spring
                alert_seed.append((bird, "Spring (Molting)", day, "Emergency", spring_em[idx][0], spring_em[idx][1].replace("{bird}", bird), json.dumps(spring_em[idx][2]), spring_em[idx][3]))
                alert_seed.append((bird, "Spring (Molting)", day, "Disease", spring_dis[idx][0], spring_dis[idx][1].replace("{bird}", bird), json.dumps(spring_dis[idx][2]), spring_dis[idx][3]))

        cursor.executemany("INSERT INTO alert_bank (bird_type, season, day_number, alert_type, title, description, options, answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", alert_seed)

    # USER-SPECIFIC COURSE PROGRESS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_course_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            progress REAL
        )
    """)
    
    # BIRD-SPECIFIC QUIZ QUESTIONS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bird_quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bird_type TEXT,
            module_title TEXT,
            question TEXT,
            options TEXT,
            answer TEXT
        )
    """)

    # Seed the Customized Quizzes if empty
    cursor.execute("SELECT COUNT(*) FROM bird_quiz_questions")
    if cursor.fetchone()[0] == 0:
        bird_data = []
        for bird in ["Lovebird", "Budgie", "Cockatiel", "Zebra Finch"]:
            # Diet Basics
            bird_data.append((bird, "Avian Diet Basics", f"What is the ideal base diet for a {bird}?", '["Only seeds", "Formulated micro-pellets & veggie chop", "Bread", "Fruit only"]', "Formulated micro-pellets & veggie chop"))
            bird_data.append((bird, "Avian Diet Basics", f"Which food is instantly fatal to a {bird}?", '["Apple", "Broccoli", "Avocado", "Carrot"]', "Avocado"))

            # Taming & Trust
            if bird == "Zebra Finch":
                bird_data.append((bird, "Taming & Trust", f"Since {bird}s are 'hands-off' observation birds, how do you reduce their stress?", '["Force them to step up", "Avoid grabbing them & move slowly", "Clip their wings", "Yell at them"]', "Avoid grabbing them & move slowly"))
            else:
                bird_data.append((bird, "Taming & Trust", f"What is the best reaction when your {bird} bites your finger?", '["Yell NO", "Flick the beak", "Stay completely calm and put them down", "Tap their head"]', "Stay completely calm and put them down"))
                bird_data.append((bird, "Taming & Trust", f"How do you teach a {bird} the 'Step-Up' command?", '["Push your finger into their chest", "Lure them with a millet treat", "Grab them", "Chase them"]', "Lure them with a millet treat"))

            # Genetics & Mutations
            bird_data.append((bird, "Genetics & Mutations", f"What does it mean if your {bird} is 'split' for a mutation?", '["It has two colors", "It carries a hidden recessive gene", "It is sick", "It is molting"]', "It carries a hidden recessive gene"))
            if bird == "Budgie":
                bird_data.append((bird, "Genetics & Mutations", "Which is a common Budgie mutation?", '["Lutino", "Cinnamon", "Pied", "All of the above"]', "All of the above"))
            elif bird == "Cockatiel":
                bird_data.append((bird, "Genetics & Mutations", "What does a Lutino Cockatiel look like?", '["Solid grey", "White/Yellow with red eyes", "Black", "Green"]', "White/Yellow with red eyes"))
            else:
                bird_data.append((bird, "Genetics & Mutations", f"Can you breed two visually mutated {bird}s together safely?", '["Yes, always", "Depends on the genetics (e.g., avoid double-lethal genes)", "No, never", "Only in summer"]', "Depends on the genetics (e.g., avoid double-lethal genes)"))

            # Danger Zones
            bird_data.append((bird, "Danger Zones", f"Why are non-stick (Teflon) pans dangerous for a {bird}?", '["They are too hot", "They release toxic PTFE gas when heated", "They reflect light", "They are heavy"]', "They release toxic PTFE gas when heated"))
            bird_data.append((bird, "Danger Zones", f"Are scented candles and essential oils safe near your {bird}?", '["Yes, they like it", "No, their respiratory systems are highly sensitive", "Only lavender", "Only in winter"]', "No, their respiratory systems are highly sensitive"))

            # Breeding Basics
            bird_data.append((bird, "Breeding Basics", f"What is a life-threatening condition where a female {bird} cannot pass an egg?", '["Egg Binding", "Crop Stasis", "Molting", "Night Fright"]', "Egg Binding"))
            bird_data.append((bird, "Breeding Basics", f"What is the most critical requirement before breeding two {bird}s?", '["Same age", "Unrelated, healthy, and on a high-calcium diet", "Fed only seeds", "Different species"]', "Unrelated, healthy, and on a high-calcium diet"))

        cursor.executemany("INSERT INTO bird_quiz_questions (bird_type, module_title, question, options, answer) VALUES (?, ?, ?, ?, ?)", bird_data)

    conn.commit()
    conn.close()

def get_daily_alerts(bird, season, day_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, alert_type, title, description, options, answer FROM alert_bank WHERE bird_type = ? AND season = ? AND day_number = ?", (bird, season, day_number))
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for r in rows:
        alerts.append({
            "db_id": str(r[0]),
            "type": r[1],
            "title": r[2],
            "desc": r[3],
            "options": json.loads(r[4]),
            "ans": r[5]
        })
    return alerts

# --- ONBOARDING & PROFILE FUNCTIONS ---
def check_onboarding_status(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT onboarding_completed FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == 1:
        return True
    return False

def save_onboarding_data(user_id, bird, experience, goal, knowledge_level="Beginner"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET selected_bird = ?, experience = ?, goal = ?, knowledge_level = ?, onboarding_completed = 1 
        WHERE id = ?
    """, (bird, experience, goal, knowledge_level, user_id))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT selected_bird, current_season_day, knowledge_level, experience, goal FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def unlock_next_day(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_season_day FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        current_day = row[0] or 1
        if current_day < 7:
            cursor.execute("UPDATE users SET current_season_day = ? WHERE id = ?", (current_day + 1, user_id))
            conn.commit()
    conn.close()

# --- DATABASE STATE SESSION CONFIG ---
def set_active_session(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_session")
    cursor.execute("INSERT INTO active_session (id, user_id, name) VALUES (1, ?, ?)", (user_id, name))
    conn.commit()
    conn.close()

def clear_active_session():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_session")
    conn.commit()
    conn.close()

def get_active_session():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name FROM active_session WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row

# --- AUTHENTICATION MODULE ---
def create_user(name, email, raw_password):
    conn = get_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    
    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (name, email, hashed_pw.decode('utf-8')))
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()

def verify_user(email, raw_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, name, stored_hash = user
        if bcrypt.checkpw(raw_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, user_id, name
    return False, None, "Invalid email or password."

# --- POCKET VET ENGINE MATH ---
def create_chat(chat_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()
    conn.close()

def update_chat_title(chat_id, new_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))
    conn.commit()
    conn.close()

def save_message(chat_id, role, text_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (chat_id, role, text_content) VALUES (?, ?, ?)", (chat_id, role, text_content))
    conn.commit()
    conn.close()

def get_all_chats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM chats")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1]} for row in rows]

def get_chat_messages(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, text_content FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "text": row[1]} for row in rows]

# --- FLOCK FLOW LOGIC (Forgiving Test-Mode Scoring) ---
def get_routine_for_date(user_id, state_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, completed, completed_time, score FROM routine_tasks WHERE user_id = ? AND state_key = ?", (user_id, state_key))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"done": bool(row[1]), "time": row[2], "score": row[3] or 0} for row in rows}

def update_routine_task(user_id, state_key, title, completed):
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now()
    current_time_str = now.strftime("%a, %I:%M %p") if completed else None
    score = 0
    
    # The Forgiving Scoring Algorithm
    if completed:
        hour = now.hour
        if "Evening" in title or "Night" in title:
            # Evening Task Target: 5:00 PM to 8:59 PM (17:00 - 20:59)
            if 17 <= hour <= 20: score = 10
            elif hour == 21: score = 8
            else: score = 5 
        else:
            # Morning Task Target: Before 10:59 AM
            if hour <= 10: score = 10
            elif hour <= 12: score = 8
            else: score = 5 
    
    cursor.execute("SELECT id FROM routine_tasks WHERE user_id = ? AND state_key = ? AND title = ?", (user_id, state_key, title))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("UPDATE routine_tasks SET completed = ?, completed_time = ?, score = ? WHERE id = ?", (int(completed), current_time_str, score, row[0]))
    else:
        cursor.execute("INSERT INTO routine_tasks (user_id, state_key, title, completed, completed_time, date_str, score) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, state_key, title, int(completed), current_time_str, state_key, score))
        
    conn.commit()
    conn.close()
    return current_time_str, score

def get_routine_history_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date_str, COUNT(id) as total_tasks, SUM(completed) as completed_tasks 
        FROM routine_tasks 
        GROUP BY date_str 
        ORDER BY date_str DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"date": row[0], "total": row[1], "completed": row[2] or 0} for row in rows]

# --- EMERGENCY ALERTS LOGIC ---
def get_alerts_for_date(user_id, state_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT alert_id, passed FROM emergency_alerts WHERE user_id = ? AND state_key = ?", (user_id, state_key))
    rows = cursor.fetchall()
    conn.close()
    return {str(row[0]): bool(row[1]) for row in rows}

def update_alert_status(user_id, state_key, alert_id, passed):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM emergency_alerts WHERE user_id = ? AND state_key = ? AND alert_id = ?", (user_id, state_key, str(alert_id)))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("UPDATE emergency_alerts SET passed = ? WHERE id = ?", (int(passed), row[0]))
    else:
        cursor.execute("INSERT INTO emergency_alerts (user_id, state_key, alert_id, passed) VALUES (?, ?, ?, ?)", (user_id, state_key, str(alert_id), int(passed)))
        
    conn.commit()
    conn.close()

# --- ⚡ FLIGHT SCHOOL ACADEMICS (User-Specific & Bird-Specific) ⚡ ---
def get_course_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, progress FROM user_course_progress WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def update_course_progress(user_id, title, progress):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_course_progress WHERE user_id = ? AND title = ?", (user_id, title))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE user_course_progress SET progress = ? WHERE id = ?", (progress, row[0]))
    else:
        cursor.execute("INSERT INTO user_course_progress (user_id, title, progress) VALUES (?, ?, ?)", (user_id, title, progress))
    conn.commit()
    conn.close()

def get_quiz_questions(bird_type, module_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, options, answer FROM bird_quiz_questions WHERE bird_type = ? AND module_title = ?", (bird_type, module_title))
    rows = cursor.fetchall()
    conn.close()
    questions = []
    for row in rows:
        questions.append({"question": row[0], "options": json.loads(row[1]), "answer": row[2]})
    return questions