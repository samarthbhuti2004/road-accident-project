import os
import math
from datetime import datetime

import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "accident_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "dataset", "indian_roads_dataset.csv")

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


# Allow the mobile app (served from another port/domain) to call the API
@app.after_request
def add_cors_headers(response):
    if request.path.startswith("/api/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# Load trained ML model
model = joblib.load(MODEL_PATH)


# -------------------------------
# Home Page
# -------------------------------
@app.route("/")
def home():
    return render_template("frontend/index.html")


# -------------------------------
# Mobile app (served by Flask so it works on the same Wi-Fi)
# -------------------------------
MOBILE_DIR = os.path.join(BASE_DIR, "mobile_app")


@app.route("/mobile/")
def mobile_home():
    return send_from_directory(MOBILE_DIR, "index.html")


@app.route("/mobile/<path:filename>")
def mobile_files(filename):
    return send_from_directory(MOBILE_DIR, filename)


# -------------------------------
# Dashboard
# -------------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("frontend/dashboard.html")


# -------------------------------
# Accident Risk Map
# -------------------------------
# --------------------------------------
# Accident Risk Map
# --------------------------------------

# --------------------------------------
# Accident Risk Map
# --------------------------------------

@app.route("/map")
def accident_map():
    return render_template(
        "frontend/map.html",
        accidents=build_city_stats()
    )


# --------------------------------------
# Accident Severity Prediction
# --------------------------------------


# --------------------------------------
# Accident Severity Prediction
# --------------------------------------
     
@app.route("/risk", methods=["GET", "POST"])
def risk():

    prediction = None

    if request.method == "POST":

        data = {
            "city": request.form["city"],
            "state": request.form["state"],
            "latitude": float(request.form["latitude"]),
            "longitude": float(request.form["longitude"]),
            "hour": int(request.form["hour"]),
            "is_weekend": int(request.form["is_weekend"]),
            "road_type": request.form["road_type"],
            "lanes": int(request.form["lanes"]),
            "traffic_signal": int(request.form["traffic_signal"]),
            "weather": request.form["weather"],
            "visibility": request.form["visibility"],
            "temperature": float(request.form["temperature"]),
            "traffic_density": request.form["traffic_density"],
            "cause": request.form["cause"],
            "is_peak_hour": int(request.form["is_peak_hour"]),
            "festival": request.form["festival"]
        }

        prediction = model.predict(pd.DataFrame([data]))[0]

    return render_template(
        "frontend/risk.html",
        prediction=prediction
    )




# =====================================================
# City statistics + explanations (used by web map AND mobile app)
# =====================================================
HAZARD_BY_CAUSE = {
    "poor road":     ("Poor road surface / potholes", "pothole.jpg"),
    "overspeeding":  ("Over-speeding on busy roads", "heavy_traffic.jpg"),
    "distraction":   ("Distracted driving in traffic", "heavy_traffic.jpg"),
    "drunk driving": ("Drunk driving / unsafe night driving", "road_construction.jpg"),
}


def hour_label(h):
    h = int(h)
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def build_city_stats():
    """Per-city statistics, risk level and a data-based reason for that level."""
    d = _df.copy()
    d["serious"] = d["accident_severity"].isin(["major", "fatal"])
    d["is_fatal"] = d["accident_severity"] == "fatal"
    overall = d["serious"].mean() * 100

    rows = []
    for (city, state), g in d.groupby(["city", "state"]):
        n = len(g)
        causes = g["cause"].value_counts()
        cause = causes.index[0]
        weather_counts = g["weather"].value_counts()
        bad_weather = "rain" if weather_counts.get("rain", 0) >= weather_counts.get("fog", 0) else "fog"

        # Hazard text + image come from the city's most common cause,
        # road type and traffic density
        top_road = g["road_type"].value_counts().index[0]
        top_density = g["traffic_density"].value_counts().index[0]

        if cause == "weather":
            if bad_weather == "rain":
                hazard, image = "Rain / water-logged roads", "water_road.jpg"
            else:
                hazard, image = "Fog / low visibility", "fog.jpg"
        elif cause == "poor road":
            if top_road == "urban":
                hazard, image = "Poor roads and road works in the city", "road_construction.jpg"
            elif top_road == "highway":
                hazard, image = "Potholes on highways", "pothole.jpg"
            else:
                hazard, image = "Poor rural roads and bridges", "bridge_construction.jpg"
        elif cause in ("overspeeding", "distraction"):
            if top_density == "high":
                hazard, image = "Speeding / distraction in heavy traffic", "heavy_traffic.jpg"
            else:
                hazard, image = "Speeding / distraction on open roads and bridges", "bridge_construction.jpg"
        else:
            hazard, image = "Drunk driving near road works", "road_construction.jpg"
        rows.append({
            "city": city,
            "state": state,
            "latitude": float(g["latitude"].mean()),
            "longitude": float(g["longitude"].mean()),
            "accident_count": int(n),
            "serious_accidents": int(g["serious"].sum()),
            "serious_percentage": round(float(g["serious"].mean() * 100), 1),
            "fatal_percentage": round(float(g["is_fatal"].mean() * 100), 1),
            "avg_casualties": round(float(g["casualties"].mean()), 2),
            "top_cause": cause,
            "top_cause_pct": round(float(causes.iloc[0] / n * 100), 1),
            "top_road_type": g["road_type"].value_counts().index[0],
            "peak_hour": hour_label(g["hour"].value_counts().index[0]),
            "hazard_reason": hazard,
            "image_name": image,
        })

    rows.sort(key=lambda r: r["serious_percentage"], reverse=True)
    total = len(rows)
    third = math.ceil(total / 3)

    for rank, r in enumerate(rows, start=1):
        r["rank"] = rank
        r["total_cities"] = total
        r["average_serious_percentage"] = round(float(overall), 1)
        r["risk_level"] = "High" if rank <= third else "Medium" if rank <= 2 * third else "Low"

        diff = r["serious_percentage"] - overall
        direction = "above" if diff > 0 else "below"
        r["risk_reason"] = (
            f"Ranked #{rank} of {total} cities. {r['serious_percentage']}% of its accidents "
            f"were major or fatal, {abs(diff):.1f} points {direction} the {overall:.1f}% average of all cities."
        )
    return rows

# =====================================================
# JSON API  (used by the mobile app)
# =====================================================
FEATURES = [
    "city", "state", "latitude", "longitude", "hour", "is_weekend",
    "road_type", "lanes", "traffic_signal", "weather", "visibility",
    "temperature", "traffic_density", "cause", "is_peak_hour", "festival"
]

_df = pd.read_csv(DATA_PATH)

# One centre point per city (used to find the nearest city from GPS)
CITY_INFO = (
    _df.groupby("city")
    .agg(state=("state", "first"),
         latitude=("latitude", "mean"),
         longitude=("longitude", "mean"),
         temperature=("temperature", "median"))
    .reset_index()
    .to_dict(orient="records")
)

# Typical values per road type (used when the app does not send them)
ROAD_DEFAULTS = {
    road: {"lanes": int(round(g["lanes"].median())),
           "traffic_signal": int(g["traffic_signal"].mode()[0])}
    for road, g in _df.groupby("road_type")
}

VALID = {
    "weather": sorted(_df["weather"].unique()),
    "road_type": sorted(_df["road_type"].unique()),
    "visibility": sorted(_df["visibility"].unique()),
    "traffic_density": sorted(_df["traffic_density"].unique()),
    "cause": sorted(_df["cause"].unique()),
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_city(lat, lon):
    best = min(CITY_INFO, key=lambda c: haversine_km(lat, lon, c["latitude"], c["longitude"]))
    return best, haversine_km(lat, lon, best["latitude"], best["longitude"])


@app.route("/api/options")
def api_options():
    """Dropdown values the mobile app can show."""
    return jsonify({"options": VALID,
                    "cities": [c["city"] for c in CITY_INFO]})


@app.route("/api/predict", methods=["POST", "OPTIONS"])
def api_predict():
    if request.method == "OPTIONS":
        return ("", 204)

    body = request.get_json(silent=True) or {}

    # Required inputs
    for field in ["weather", "road_type", "visibility"]:
        if field not in body:
            return jsonify({"error": f"Missing field: {field}"}), 400
        body[field] = str(body[field]).lower()
        if body[field] not in VALID[field]:
            return jsonify({"error": f"Invalid {field}. Allowed: {VALID[field]}"}), 400

    # Location -> nearest city (or use a city name directly)
    try:
        lat = float(body["latitude"]) if "latitude" in body else None
        lon = float(body["longitude"]) if "longitude" in body else None
    except (TypeError, ValueError):
        return jsonify({"error": "latitude/longitude must be numbers"}), 400

    if lat is not None and lon is not None:
        city, dist = nearest_city(lat, lon)
    elif body.get("city"):
        city = next((c for c in CITY_INFO if c["city"].lower() == str(body["city"]).lower()), None)
        if city is None:
            return jsonify({"error": "Unknown city"}), 400
        lat, lon, dist = city["latitude"], city["longitude"], 0
    else:
        return jsonify({"error": "Send latitude+longitude or city"}), 400

    # Time features (taken from the phone's clock unless sent)
    now = datetime.now()
    hour = int(body.get("hour", now.hour))
    is_weekend = int(body.get("is_weekend", 1 if now.weekday() >= 5 else 0))
    is_peak = int(body.get("is_peak_hour", 1 if hour in (7, 8, 9, 17, 18, 19, 20) else 0))

    defaults = ROAD_DEFAULTS[body["road_type"]]
    row = {
        "city": city["city"],
        "state": city["state"],
        "latitude": lat,
        "longitude": lon,
        "hour": hour,
        "is_weekend": is_weekend,
        "road_type": body["road_type"],
        "lanes": int(body.get("lanes", defaults["lanes"])),
        "traffic_signal": int(body.get("traffic_signal", defaults["traffic_signal"])),
        "weather": body["weather"],
        "visibility": body["visibility"],
        "temperature": float(body.get("temperature", city["temperature"])),
        "traffic_density": str(body.get("traffic_density", "medium")).lower(),
        "cause": str(body.get("cause", "distraction")).lower(),
        "is_peak_hour": is_peak,
        "festival": body.get("festival", "Unknown"),   # model was trained with "Unknown" for no festival
    }

    X = pd.DataFrame([row])[FEATURES]
    probs = model.predict_proba(X)[0]
    classes = list(model.classes_)
    probabilities = {c: round(float(p) * 100, 1) for c, p in zip(classes, probs)}
    predicted = classes[int(probs.argmax())]

    return jsonify({
        "predicted_severity": predicted,
        "probabilities": probabilities,
        "city_used": city["city"],
        "distance_to_city_km": round(dist, 1),
        "inputs_used": row,
        "note": "Prototype model trained on a synthetic dataset; not a safety guarantee."
    })


@app.route("/api/hotspots")
def api_hotspots():
    """Per-city statistics, risk level and reasons for the mobile map."""
    return jsonify(build_city_stats())


# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)