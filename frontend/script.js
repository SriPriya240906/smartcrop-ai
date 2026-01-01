const backendUrl = "http://127.0.0.1:5000";

// Global state
let cropFormData = {
  pin:"", temperature:null, humidity:null, rainfall:null,
  city:"", district:"", state:"",
  N:50, P:40, K:45, PH:6.5,
  soil_type:"Alluvial", landSize:5, budget:150000,
  irrigation:"Drip", farming:"Traditional"
};

// ---------------- Growing steps for limited crops ----------------
const cropSteps = {
  "WHEAT": [
    "Sow seeds in well-prepared soil",
    "Maintain moisture during germination",
    "Apply nitrogen fertilizer after 3-4 weeks",
    "Harvest when grains turn golden brown"
  ],
  "RICE": [
    "Flood the field before transplanting seedlings",
    "Ensure continuous water supply",
    "Use phosphorus-rich fertilizer at tillering stage",
    "Harvest when grains are firm"
  ],
  "MAIZE": [
    "Plant seeds 2-3 cm deep in loose soil",
    "Irrigate regularly during flowering",
    "Apply potassium fertilizer at early growth stage",
    "Harvest when cobs mature"
  ]
  // Add more crops as needed
};

// ---------------- Update sliders ----------------
["N","P","K","PH"].forEach(id=>{
  const input = document.getElementById(`input${id}`);
  const span = document.getElementById(id);
  input.addEventListener("input", e=>{ 
    cropFormData[id] = +e.target.value;
    span.innerText = e.target.value;
  });
});

// Soil type
const soilType = document.getElementById("soilType");
soilType.addEventListener("change", e=> cropFormData.soil_type=e.target.value);

// Irrigation
document.querySelectorAll(".irrigation-card").forEach(card=>{
  card.addEventListener("click", ()=>{
    document.querySelectorAll(".irrigation-card").forEach(c=>c.classList.remove("active"));
    card.classList.add("active");
    cropFormData.irrigation = card.dataset.irrigation;
  });
});

// Farming
document.querySelectorAll(".farming-card").forEach(card=>{
  card.addEventListener("click", ()=>{
    document.querySelectorAll(".farming-card").forEach(c=>c.classList.remove("active"));
    card.classList.add("active");
    cropFormData.farming = card.dataset.method;
  });
});

// Budget slider
const budgetInput = document.getElementById("budgetInput");
budgetInput.addEventListener("input", e=>{
  cropFormData.budget = +e.target.value;
  document.getElementById("budget").innerText = (+e.target.value).toLocaleString();
});

// ---------------- Fetch climate ----------------
document.getElementById("fetchClimateBtn").addEventListener("click", async ()=>{
  const pin = document.getElementById("pinCode").value.trim();
  if(pin.length!==6){ alert("Enter valid PIN"); return; }
  try{
    const res = await fetch(`${backendUrl}/climate/${pin}`);
    const data = await res.json();
    if(!res.ok){ alert(data.error||"Climate fetch failed"); return; }
    cropFormData.pin=pin;
    cropFormData.temperature=data.temperature;
    cropFormData.humidity=data.humidity;
    cropFormData.rainfall=data.rainfall;
    cropFormData.city=data.city;
    cropFormData.district=data.district;
    cropFormData.state=data.state;

    document.getElementById("temperature").innerText=Math.round(data.temperature);
    document.getElementById("humidity").innerText=Math.round(data.humidity);
    document.getElementById("rainfall").innerText=Math.round(data.rainfall);
    document.getElementById("city").value=data.city;
    document.getElementById("district").value=data.district;
    document.getElementById("state").value=data.state;
  } catch(err){ console.error(err); alert("Backend not running"); }
});

// ---------------- Analyze & show crop ----------------
document.getElementById("analyzeBtn").addEventListener("click", async ()=>{
  const btn=document.getElementById("analyzeBtn");
  const stepsList = document.getElementById("growingSteps");
  btn.disabled=true; btn.innerText="Analyzing...";
  stepsList.innerHTML = ""; // Clear previous steps

  try{
    const res = await fetch(`${backendUrl}/predict`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({
        N:cropFormData.N,
        P:cropFormData.P,
        K:cropFormData.K,
        temperature:cropFormData.temperature,
        humidity:cropFormData.humidity,
        rainfall:cropFormData.rainfall,
        ph:cropFormData.PH,
        soil_type:cropFormData.soil_type
      })
    });
    const data = await res.json();
    if(!res.ok || !data.recommended_crop){
      alert("Prediction failed");
      document.getElementById("recommendedCrop").innerText="Prediction failed";
      return;
    }

    const cropName = data.recommended_crop.toUpperCase();
    document.getElementById("recommendedCrop").innerText = cropName;

    // Show growing steps if available
    if(cropSteps[cropName]){
      cropSteps[cropName].forEach(step=>{
        const li = document.createElement("li");
        li.textContent = step;
        stepsList.appendChild(li);
      });
    }

  } catch(err){
    console.error(err);
    document.getElementById("recommendedCrop").innerText="Request interrupted";
    alert("Request interrupted");
  } finally{
    btn.disabled=false; btn.innerText="Analyze & Recommend Crop";
  }
});

