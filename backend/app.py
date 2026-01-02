from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib, pandas as pd, requests


app = Flask(__name__)
CORS(app)
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")



def get_location_from_opencage(pincode):
    try:
        url=f"https://api.opencagedata.com/geocode/v1/json?q={pincode},India&key={OPENCAGE_API_KEY}&language=en&limit=1"
        res=requests.get(url,timeout=8).json()
        if res.get("results"):
            comp=res["results"][0]["components"]
            city=comp.get("city") or comp.get("town") or comp.get("village") or comp.get("county") or "Unknown"
            district=comp.get("state_district") or comp.get("county") or city
            state=comp.get("state") or "Unknown"
            lat=res["results"][0]["geometry"]["lat"]
            lon=res["results"][0]["geometry"]["lng"]
            return city,district,state,lat,lon
    except: pass
    return "Unknown","Unknown","Unknown",20.5937,78.9629

print("Loading ML model...")
model=joblib.load("model.pkl")
print("✅ Model loaded")

SOIL_COLUMNS=["soil_type_Alluvial","soil_type_Black","soil_type_Laterite","soil_type_Red"]

@app.route("/climate/<pincode>")
def climate(pincode):
    city,district,state,lat,lon=get_location_from_opencage(pincode)
    if lat is None or lon is None: return jsonify({"error":"Invalid PIN"}),400
    try:
        nasa_url=f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR,RH2M&community=AG&latitude={lat}&longitude={lon}&start=20220101&end=20221231&format=JSON"
        res=requests.get(nasa_url,timeout=10).json()
        if "properties" not in res: return jsonify({"error":"NASA API unavailable"}),500
        p=res["properties"]["parameter"]
        temp=sum(p["T2M"].values())/len(p["T2M"])
        hum=sum(p["RH2M"].values())/len(p["RH2M"])
        rain=sum(p["PRECTOTCORR"].values())
        return jsonify({"temperature":round(temp,1),"humidity":round(hum,1),"rainfall":round(rain,1),
                        "city":city,"district":district,"state":state})
    except: return jsonify({"error":"Climate fetch failed"}),500

@app.route("/predict",methods=["POST"])
def predict():
    data=request.json
    if not data.get("temperature") or not data.get("rainfall"): return jsonify({"error":"Climate missing"}),400
    soil_type=data.get("soil_type","Alluvial")
    soil_input=[0]*len(SOIL_COLUMNS)
    soil_col=f"soil_type_{soil_type.capitalize()}"
    if soil_col in SOIL_COLUMNS: soil_input[SOIL_COLUMNS.index(soil_col)]=1
    features={"N":data["N"],"P":data["P"],"K":data["K"],
              "temperature":data["temperature"],"humidity":data["humidity"],
              "ph":data["ph"],"rainfall":data["rainfall"]}
    for i,col in enumerate(SOIL_COLUMNS): features[col]=soil_input[i]
    df=pd.DataFrame([features])
    print("🔮 ML prediction input:\n",df)
    prediction=model.predict(df)[0]
    print("✅ Predicted crop:",prediction)
    return jsonify({"recommended_crop":prediction})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

