import pandas as pd
import matplotlib.pyplot as plt
import os

# Load dataset
data = pd.read_csv("dataset/indian_roads_dataset.csv")

# Create output folder
os.makedirs("backend/analytics", exist_ok=True)

print("======================================")
print("   ROAD ACCIDENT DATA ANALYTICS")
print("======================================")

print("\nTotal Accident Records:", len(data))

# -------------------------------
# 1. Accident Severity
# -------------------------------
print("\nAccident Severity:")
print(data["accident_severity"].value_counts())

data["accident_severity"].value_counts().plot(
    kind="bar",
    title="Accident Severity Distribution"
)

plt.xlabel("Severity")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig("backend/analytics/severity_distribution.png")
plt.close()


# -------------------------------
# 2. Accidents by Weather
# -------------------------------
print("\nAccidents by Weather:")
print(data["weather"].value_counts())

data["weather"].value_counts().plot(
    kind="bar",
    title="Accidents by Weather"
)

plt.xlabel("Weather")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig("backend/analytics/weather_analysis.png")
plt.close()


# -------------------------------
# 3. Accidents by Road Type
# -------------------------------
print("\nAccidents by Road Type:")
print(data["road_type"].value_counts())

data["road_type"].value_counts().plot(
    kind="bar",
    title="Accidents by Road Type"
)

plt.xlabel("Road Type")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig("backend/analytics/road_type_analysis.png")
plt.close()


# -------------------------------
# 4. Accidents by Cause
# -------------------------------
print("\nAccidents by Cause:")
print(data["cause"].value_counts())

data["cause"].value_counts().plot(
    kind="bar",
    title="Accidents by Cause"
)

plt.xlabel("Cause")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("backend/analytics/cause_analysis.png")
plt.close()


# -------------------------------
# 5. Accidents by Hour
# -------------------------------
print("\nAccidents by Hour:")

hour_counts = data["hour"].value_counts().sort_index()
print(hour_counts)

hour_counts.plot(
    kind="line",
    marker="o",
    title="Accidents by Hour"
)

plt.xlabel("Hour")
plt.ylabel("Number of Accidents")
plt.grid(True)
plt.tight_layout()
plt.savefig("backend/analytics/hour_analysis.png")
plt.close()


# -------------------------------
# 6. Accidents by City
# -------------------------------
print("\nTop Accident Locations:")

city_counts = data["city"].value_counts()

print(city_counts.head(10))

city_counts.head(10).plot(
    kind="bar",
    title="Top 10 Accident-Prone Cities"
)

plt.xlabel("City")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("backend/analytics/top_cities.png")
plt.close()


print("\n======================================")
print("ANALYTICS COMPLETED SUCCESSFULLY")
print("======================================")
print("Charts saved inside:")
print("backend/analytics/")