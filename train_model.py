import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import m2cgen as m2c

# 1. Load the Synthetic Data
print("Loading AvianQuest data...")
df = pd.read_csv('avianquest_training_data.csv')

# 2. Separate the Inputs (X) from the Answer (y)
X = df.drop('Risk_Class', axis=1) # The 7 routine features
y = df['Risk_Class']              # The final risk prediction

# 3. The 80/20 Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training on {len(X_train)} rows, Testing on {len(X_test)} rows.\n")

# 4. Initialize and Train the Random Forest Model
# PRO TIP: We limit max_depth to 5 so the final Python file doesn't become too huge for mobile!
model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# 5. Test the Model (The Final Exam)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("=== AI EXAM RESULTS ===")
print(f"Model Accuracy: {accuracy * 100:.2f}%\n")
print("Detailed Breakdown:")
print(classification_report(y_test, predictions))

# 6. Transpile to Pure Python for your Flet App!
print("Converting AI model to pure Python for mobile edge-computing...")
pure_python_code = m2c.export_to_python(model)

# Save it to a new file that you will use in your Flet app
with open("avian_ai_brain.py", "w") as f:
    f.write(pure_python_code)

print("\nSUCCESS: Saved trained model as 'avian_ai_brain.py'!")