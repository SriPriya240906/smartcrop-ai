# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

print("Loading dataset...")

# Load dataset
data = pd.read_csv("final_crop_reduced.csv", encoding="latin1")

# Remove missing values
data = data.dropna()

# One-hot encode soil_type
data = pd.get_dummies(data, columns=["soil_type"])

# ✅ FORCE FEATURE ORDER (VERY IMPORTANT)
FEATURE_ORDER = [
    "N", "P", "K",
    "temperature", "humidity", "ph", "rainfall",
    "soil_type_Alluvial",
    "soil_type_Black",
    "soil_type_Laterite",
    "soil_type_Red"
]

X = data[FEATURE_ORDER]
y = data["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training model...")

# RandomForest (fast + stable)
model = RandomForestClassifier(
    n_estimators=50,
    random_state=42,
    n_jobs=1
)

model.fit(X_train, y_train)

print("✅ Model trained successfully")

accuracy = model.score(X_test, y_test)
print("✅ Model Accuracy:", accuracy)

# Save compressed model
joblib.dump(model, "model.pkl", compress=3)

print("✅ Model saved as model.pkl")
