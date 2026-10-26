import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# Load dataset
data = pd.read_csv("dataset/indian_roads_dataset.csv")

features = [
    "city", "state", "latitude", "longitude",
    "hour", "is_weekend", "road_type", "lanes",
    "traffic_signal", "weather", "visibility",
    "temperature", "traffic_density", "cause",
    "is_peak_hour", "festival"
]

target = "accident_severity"

df = data[features + [target]].dropna(subset=[target])

X = df[features].copy()
y = df[target]

# Identify categorical and numerical columns
categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_features = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

# Fill missing values
for column in categorical_features:
    X[column] = X[column].fillna("Unknown")

for column in numerical_features:
    X[column] = X[column].fillna(X[column].median())

# Preprocessing
preprocessor = ColumnTransformer([
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
])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Models
models = {
    "Decision Tree": DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    ),

    "Logistic Regression": LogisticRegression(
        max_iter=3000,
        random_state=42,
        class_weight="balanced"
    )
}

print("======================================")
print("   ML MODEL EVALUATION")
print("======================================")

for name, model in models.items():

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # Train
    pipeline.fit(X_train, y_train)

    # Predict
    predictions = pipeline.predict(X_test)

    # Metrics
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("\n--------------------------------------")
    print(name)
    print("--------------------------------------")

    print("Accuracy  :", round(accuracy * 100, 2), "%")
    print("Precision :", round(precision * 100, 2), "%")
    print("Recall    :", round(recall * 100, 2), "%")
    print("F1-Score  :", round(f1 * 100, 2), "%")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))

print("\n======================================")
print("   EVALUATION COMPLETED")
print("======================================")