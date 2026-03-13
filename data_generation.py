import random
import pandas as pd

def generate_synthetic_data(num_samples=10000):
    data = []
    
    # Optional: Set a seed so your data is reproducible every time you run it
    random.seed(42) 
    
    for _ in range(num_samples):
        # ==========================================
        # 1. REALISTIC HUMAN BEHAVIOR GENERATION
        # ==========================================
        
        # 80% remember morning care, 20% forget completely
        morning_care_completed = random.choices([1, 0], weights=[80, 20])[0] 
        
        if morning_care_completed == 1:
            # If they remembered, most are 0-30 mins late. Very few are 180 mins late.
            # Using a triangular distribution: (min=0, max=180, peak/mode=15)
            morning_care_delay = int(random.triangular(0, 180, 15)) 
        else:
            # If they forgot completely, the delay is maxed out
            morning_care_delay = 180
            
        # Most clean the cage daily (0 days) or 1 day. Rare to go 5 days.
        uncleaned_days = random.choices([0, 1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 3, 2])[0]
        
        # Seasons are equally likely (1=Winter, 2=Spring, 3=Summer, 4=Autumn)
        season = random.choice([1, 2, 3, 4]) 
        
        # 90% remember to put the night cover on
        night_cover = random.choices([1, 0], weights=[90, 10])[0] 
        
        # Quiz scores: Bell curve (Normal Distribution) around 70% average
        quiz_score = int(random.gauss(70, 15)) 
        quiz_score = max(0, min(100, quiz_score)) # Clamp between 0 and 100
        
        # Chat scores: Bell curve around 6 (Neutral/Good questions)
        chat_score = int(random.gauss(6, 2))
        chat_score = max(0, min(10, chat_score)) # Clamp between 0 and 10

        # ==========================================
        # 2. BIOLOGICAL RULES (TRUTH TABLE)
        # ==========================================
        
        # Rule A: Critical Danger (Immediate threat to life)
        if (morning_care_completed == 0) or (morning_care_delay >= 120) or (uncleaned_days >= 4 and season == 3) or (night_cover == 0 and season == 1) or (quiz_score < 30) or (chat_score <= 2):
            risk_class = 3  # Class 3: Critical Danger
            
        # Rule B: Severe Risk (Major neglect, but not immediately fatal)
        elif (morning_care_completed == 1) and ((morning_care_delay >= 60 and morning_care_delay < 120) or (uncleaned_days >= 2 and season != 3) or (night_cover == 0 and season == 4) or (quiz_score >= 30 and quiz_score < 60) or (chat_score >= 3 and chat_score <= 5)):
            risk_class = 2  # Class 2: Severe Risk
            
        # Rule C: Mild Stress (Minor mistakes)
        elif (morning_care_completed == 1) and ((morning_care_delay > 0 and morning_care_delay < 60) or (uncleaned_days == 1 and season in [1, 2, 3, 4]) or (night_cover == 1 and season == 3) or (quiz_score >= 60 and quiz_score < 80) or (chat_score >= 6 and chat_score <= 8)):
            risk_class = 1  # Class 1: Mild Stress
            
        # Rule D: Optimal Health (Perfect Care)
        elif (morning_care_completed == 1) and (morning_care_delay == 0) and (uncleaned_days == 0) and (season in [1, 2, 3, 4]) and (night_cover == 1 or season != 1) and (quiz_score >= 80) and (chat_score >= 9):
            risk_class = 0  # Class 0: Optimal Health
            
        # Fallback (Catches any bizarre edge cases)
        else:
            risk_class = 1

        # ==========================================
        # 3. SAVE THE VIRTUAL DAY
        # ==========================================
        data.append([morning_care_completed, morning_care_delay, uncleaned_days, season, night_cover, quiz_score, chat_score, risk_class])

    # ==========================================
    # 4. EXPORT TO CSV
    # ==========================================
    columns = ['Morning_Care_Completed', 'Morning_Care_Delay_Mins', 'Uncleaned_Days', 'Season', 'Night_Cover', 'Quiz_Score', 'Chat_Score', 'Risk_Class']
    df = pd.DataFrame(data, columns=columns)
    
    df.to_csv('avianquest_training_data.csv', index=False)
    print(f"Successfully generated {num_samples} rows of Master-Level AI training data!")

# Run the generator
if __name__ == "__main__":
    generate_synthetic_data(10000)