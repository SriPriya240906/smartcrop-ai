import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "N": 20,
    "P": 20,
    "K": 20,
    "temperature": 34,
    "humidity": 45,
    "ph": 7.8,
    "rainfall": 70,
    "soil_type": "Black"
}


response = requests.post(url, json=data)
print(response.json())
