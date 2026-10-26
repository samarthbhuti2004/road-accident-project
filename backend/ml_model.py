import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# Load dataset
data = pd.read_csv("dataset/indian_roads_dataset.csv")

# Features
features = [
    "city",
    "state",
    "latitude",
    "longitude",
    "hour",
    "is_weekend",
    "road_type",
    "lanes",
    "traffic_signal",
    "weather",
    "visibility",
    "temperature",
    "traffic_density",
    "cause",
    "is_peak_hour",
    "festival"
]

target = "accident_severity"

# Keep required columns
df = data[features + [target]].copy()

# Remove rows where target is missing
df = df.dropna(subset=[target])

# Separate input and target
X = df[features]
y = df[target]

# Automatically identify text and numeric columns
categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
numerical_features = X.select_dtypes(exclude=["object"]).columns.tolist()

# Fill missing values
for column in categorical_features:
    X[column] = X[column].fillna("Unknown")

for column in numerical_features:
    X[column] = X[column].fillna(X[column].median())

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)

# Random Forest model (min_samples_leaf keeps the saved model small)
model = RandomForestClassifier(
    n_estimators=100,
    min_samples_leaf=5,
    random_state=42
)

# ML pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Train
pipeline.fit(X_train, y_train)

# Predict
predictions = pipeline.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print("======================================")
print("   ROAD ACCIDENT ML MODEL")
print("======================================")
print("Total records used :", len(df))
print("Training records   :", len(X_train))
print("Testing records    :", len(X_test))
print("Categorical inputs :", categorical_features)
print("Numeric inputs     :", numerical_features)
print("Model Accuracy     :", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save model (compress=3 makes the file much smaller)
joblib.dump(pipeline, "backend/accident_model.pkl", compress=3)

print("\nModel saved successfully!")