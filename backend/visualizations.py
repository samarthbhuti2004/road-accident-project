import pandas as pd
import matplotlib.pyplot as plt
import os

# Load dataset
data = pd.read_csv("dataset/indian_roads_dataset.csv")

# Create folder for charts
chart_folder = "backend/static/charts"
os.makedirs(chart_folder, exist_ok=True)

print("======================================")
print("   ROAD ACCIDENT VISUAL ANALYTICS")
print("======================================")

# 1. Accident Severity
severity = data["accident_severity"].value_counts()

plt.figure(figsize=(8, 5))
severity.plot(kind="bar")
plt.title("Accidents by Severity")
plt.xlabel("Accident Severity")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig(f"{chart_folder}/severity.png")
plt.close()

# 2. Weather
weather = data["weather"].value_counts()

plt.figure(figsize=(8, 5))
weather.plot(kind="bar")
plt.title("Accidents by Weather")
plt.xlabel("Weather")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig(f"{chart_folder}/weather.png")
plt.close()

# 3. Road Type
road_type = data["road_type"].value_counts()

plt.figure(figsize=(8, 5))
road_type.plot(kind="bar")
plt.title("Accidents by Road Type")
plt.xlabel("Road Type")
plt.ylabel("Number of Accidents")
plt.tight_layout()
plt.savefig(f"{chart_folder}/road_type.png")
plt.close()

# 4. Accident Cause
cause = data["cause"].value_counts()

plt.figure(figsize=(9, 5))
cause.plot(kind="bar")
plt.title("Accidents by Cause")
plt.xlabel("Cause")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{chart_folder}/cause.png")
plt.close()

# 5. Accidents by Hour
hour = data["hour"].value_counts().sort_index()

plt.figure(figsize=(10, 5))
hour.plot(kind="line", marker="o")
plt.title("Accidents by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Accidents")
plt.xticks(range(0, 24))
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{chart_folder}/hour.png")
plt.close()

# 6. Top Accident Locations
city = data["city"].value_counts().head(10)

plt.figure(figsize=(10, 6))
city.plot(kind="bar")
plt.title("Top 10 Accident-Prone Cities")
plt.xlabel("City")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{chart_folder}/top_cities.png")
plt.close()

print("\nCharts created successfully!")

print("\nCharts saved in:")
print("backend/static/charts/")

print("\nCreated files:")
print("1. severity.png")
print("2. weather.png")
print("3. road_type.png")
print("4. cause.png")
print("5. hour.png")
print("6. top_cities.png")

print("\n======================================")
print("   VISUALIZATION COMPLETED")
print("======================================")