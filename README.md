# Road Accident Data Analytics & Severity Prediction (ML + Mobile App)

## Run (Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```
- Web app:    http://localhost:5000
- Mobile app: http://localhost:5000/mobile/
- API: GET /api/options, GET /api/hotspots, POST /api/predict

## Test on your phone (same Wi-Fi)
1. Find your PC's IP (`ipconfig`, e.g. 192.168.1.8).
2. Open http://192.168.1.8:5000/mobile/ on the phone.
   (GPS needs HTTPS, so on plain http use the "City" dropdown.)

## Example API call
POST /api/predict
{"city":"Delhi","weather":"rain","road_type":"urban","visibility":"low","traffic_density":"high"}
(or send "latitude" and "longitude" instead of "city")

## Re-train / regenerate
```
python backend/ml_model.py
python backend/model_comparison.py
python backend/analytics.py
python backend/visualizations.py
```
Run these from the project root folder.

## Note
Dataset is synthetic, so model accuracy is modest (~53% Random Forest).
