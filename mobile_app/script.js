// ---------------------------------------------------------------
// API address.
//  - Opened from Flask (http://<pc-ip>:5000/mobile/) -> leave as "".
//  - Hosted elsewhere (e.g. APK / Netlify) -> put your backend URL,
//    e.g. "https://your-app.onrender.com"
// ---------------------------------------------------------------
const API_BASE = "";

const $ = (id) => document.getElementById(id);
const locationBtn = $("locationBtn");
const locationResult = $("locationResult");
const predictionForm = $("predictionForm");
const predictionResult = $("predictionResult");

let userLat = null;
let userLon = null;

// ---------- helpers ----------
async function api(path, options) {
  const res = await fetch(API_BASE + path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Server error");
  return data;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

const SEVERITY_INFO = {
  fatal: { label: "Fatal risk", cls: "sev-fatal", icon: "🔴" },
  major: { label: "Major risk", cls: "sev-major", icon: "🟠" },
  minor: { label: "Minor risk", cls: "sev-minor", icon: "🟢" }
};

// ---------- connection check + city list ----------
async function init() {
  try {
    const data = await api("/api/options");
    data.cities.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      $("city").appendChild(opt);
    });
    $("apiStatus").textContent = "● Online";
    $("apiStatus").classList.add("online");
    loadHotspots();
  } catch (e) {
    $("apiStatus").textContent = "● Offline";
    $("apiStatus").classList.add("offline");
    predictionResult.textContent =
      "Cannot reach the server. Start the Flask backend and check API_BASE in script.js.";
  }
}

// ---------- GPS ----------
locationBtn.addEventListener("click", function () {
  if (!navigator.geolocation) {
    locationResult.textContent = "Location is not supported. Please choose a city instead.";
    return;
  }
  locationResult.textContent = "Requesting location permission...";
  navigator.geolocation.getCurrentPosition(
    function (pos) {
      userLat = pos.coords.latitude;
      userLon = pos.coords.longitude;
      locationResult.textContent =
        `Latitude: ${userLat.toFixed(5)}, Longitude: ${userLon.toFixed(5)}`;
      $("city").value = "";
    },
    function () {
      locationResult.textContent =
        "Location unavailable. Allow permission (GPS needs HTTPS or localhost), or choose a city below.";
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
});

// ---------- prediction ----------
predictionForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const payload = {
    weather: $("weather").value,
    road_type: $("road").value,
    visibility: $("visibility").value,
    traffic_density: $("traffic").value
  };

  const chosenCity = $("city").value;
  if (chosenCity) {
    payload.city = chosenCity;
  } else if (userLat !== null) {
    payload.latitude = userLat;
    payload.longitude = userLon;
  } else {
    predictionResult.textContent = "Tap “Get My Location” or choose a city first.";
    return;
  }

  // Time features from the phone clock
  const now = new Date();
  const hour = now.getHours();
  const day = now.getDay();
  payload.hour = hour;
  payload.is_weekend = day === 0 || day === 6 ? 1 : 0;
  payload.is_peak_hour = [7, 8, 9, 17, 18, 19, 20].includes(hour) ? 1 : 0;

  $("predictBtn").disabled = true;
  predictionResult.textContent = "Predicting…";

  try {
    const r = await api("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const info = SEVERITY_INFO[r.predicted_severity];
    const bars = ["fatal", "major", "minor"]
      .map((k) => {
        const p = r.probabilities[k] ?? 0;
        return `<div class="bar-row"><span>${k}</span>
          <div class="bar"><div class="fill ${SEVERITY_INFO[k].cls}" style="width:${p}%"></div></div>
          <span>${p}%</span></div>`;
      })
      .join("");

    predictionResult.innerHTML =
      `<div class="badge ${info.cls}">${info.icon} ${info.label}</div>` +
      `<p class="small">Based on ${escapeHtml(r.city_used)} · ${hour}:00 · ` +
      `${payload.is_peak_hour ? "peak hour" : "off-peak"}</p>` + bars;
  } catch (err) {
    predictionResult.textContent = "Error: " + err.message;
  } finally {
    $("predictBtn").disabled = false;
  }
});

// ---------- hotspot map ----------
let map = null;
const markers = {};
const RISK_COLOR = { High: "#d32f2f", Medium: "#f57c00", Low: "#2e7d32" };

function popupHtml(s) {
  return (
    `<div class="pop">` +
    `<b>${escapeHtml(s.city)}, ${escapeHtml(s.state)}</b> ` +
    `<span class="badge b-${s.risk_level}">${s.risk_level}</span>` +
    `<table>` +
    `<tr><td>Accidents</td><td>${s.accident_count}</td></tr>` +
    `<tr><td>Serious</td><td>${s.serious_percentage}%</td></tr>` +
    `<tr><td>Fatal</td><td>${s.fatal_percentage}%</td></tr>` +
    `<tr><td>Top cause</td><td>${escapeHtml(s.top_cause)}</td></tr>` +
    `<tr><td>Busiest hour</td><td>${escapeHtml(s.peak_hour)}</td></tr>` +
    `</table>` +
    `<div class="why"><b>Why ${s.risk_level}?</b> ${escapeHtml(s.risk_reason)}</div>` +
    `<b>Hazard: ${escapeHtml(s.hazard_reason)}</b>` +
    `<img class="hz" width="220" height="120" alt="${escapeHtml(s.hazard_reason)}" ` +
    `src="${API_BASE}/static/charts/hazard_images/${s.image_name}">` +
    `</div>`
  );
}

async function loadHotspots() {
  try {
    const spots = await api("/api/hotspots");

    map = L.map("map").setView([22.5, 79], 4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    const list = $("hotspotList");
    list.innerHTML = "";

    spots.forEach((s) => {
      const color = RISK_COLOR[s.risk_level];
      markers[s.city] = L.circleMarker([s.latitude, s.longitude], {
        radius: 11, color: "#fff", weight: 2, fillColor: color, fillOpacity: 0.9
      })
        .addTo(map)
        .bindPopup(popupHtml(s), { maxWidth: 250, minWidth: 230, autoPanPadding: [20, 20] });

      const li = document.createElement("li");
      li.innerHTML =
        `<span class="dot" style="background:${color}"></span>` +
        `<b>${escapeHtml(s.city)}</b> <small>#${s.rank} · ${s.serious_percentage}% serious</small>` +
        `<span class="tag" style="color:${color}">${s.risk_level}</span>`;
      li.addEventListener("click", () => {
        map.setView([s.latitude, s.longitude], 8);
        markers[s.city].openPopup();
        $("map").scrollIntoView({ behavior: "smooth", block: "center" });
      });
      list.appendChild(li);
    });
  } catch (e) {
    $("map").textContent = "Could not load hotspots.";
  }
}

init();
