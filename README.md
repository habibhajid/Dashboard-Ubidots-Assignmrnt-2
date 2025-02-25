# Dashboard-Ubidots-Assignmrnt-2

# Tutorial Menjalankan Sensor DHT11 dan PIR dengan ESP32, Dashboard Ubidots, dan MongoDB

## Pendahuluan
Tutorial ini menjelaskan langkah-langkah untuk menghubungkan sensor DHT11 dan PIR ke ESP32, mengirimkan datanya ke dashboard Ubidots, serta menyimpan data tersebut di MongoDB menggunakan server Flask.

---

## 1. Peralatan yang Dibutuhkan
- ESP32
- Sensor DHT11/DHT22
- Sensor PIR
- Breadboard dan kabel jumper
- Koneksi WiFi

---

## 2. Instalasi dan Konfigurasi

### 2.1 Instalasi Perpustakaan Python
Pastikan Anda telah menginstal Python dan beberapa pustaka berikut:
```bash
pip install flask pymongo
```

---

### 2.2 Kode Server Flask (Python)
Buat file `server.py` dan salin kode berikut:

```python
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.vtbru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["sensordb"]
collection = db["sensor_data"]

@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    try:
        data = request.json
        data["timestamp"] = datetime.datetime.utcnow()
        result = collection.insert_one(data)
        return jsonify({"id": str(result.inserted_id), "message": "Data berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sensor", methods=["GET"])
def get_sensor_data():
    try:
        data = list(collection.find().sort("timestamp", -1).limit(10))
        for doc in data:
            doc["_id"] = str(doc["_id"])
            doc["timestamp"] = doc["timestamp"].isoformat()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Jalankan server dengan perintah:
```bash
python server.py
```

---

### 2.3 Kode ESP32 (MicroPython)
Unggah kode berikut ke ESP32:

```python
from machine import Pin
import dht
import network
import ujson
import utime
import urequests

# Koneksi WiFi
SSID = "<WIFI_SSID>"
PASSWORD = "<WIFI_PASSWORD>"

# Konfigurasi Sensor
DHT_PIN = 14
PIR_PIN = 27
dht_sensor = dht.DHT22(Pin(DHT_PIN))
pir_sensor = Pin(PIR_PIN, Pin.IN)

# URL Flask API
FLASK_URL = "http://10.80.3.98:5000/sensor"

# Fungsi Koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Menghubungkan ke WiFi...")
    while not wlan.isconnected():
        utime.sleep(1)
    
    print("Terhubung ke WiFi:", wlan.ifconfig())

# Fungsi untuk Membaca Sensor dengan Normalisasi Data
def read_sensors():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        if temperature < 0 or temperature > 50:
            temperature = temperature / 10  
        if humidity < 0 or humidity > 100:
            humidity = humidity / 10

    except Exception as e:
        print("Gagal membaca sensor:", str(e))
        temperature, humidity = -1, -1

    pir_value = pir_sensor.value()
    return temperature, humidity, pir_value

# Fungsi Kirim Data ke Flask API
def send_data():
    while True:
        temperature, humidity, pir_value = read_sensors()
        
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "pir_sensor": pir_value
        }
        
        try:
            response = urequests.post(FLASK_URL, json=payload)
            print("Response:", response.text)
            response.close()
        except Exception as e:
            print("Gagal mengirim data:", str(e))
        
        utime.sleep(5)  

# Program Utama
def main():
    connect_wifi()
    send_data()

if __name__ == "__main__":
    main()
```

Unggah kode ke ESP32 dan jalankan.

---

## 3. Integrasi dengan Ubidots
1. Buat akun di [Ubidots](https://ubidots.com/).
2. Tambahkan **Device** baru.
3. Buat **Variable** untuk suhu, kelembapan, dan sensor PIR.
4. Gunakan webhook atau API Ubidots untuk mengirim data dari Flask ke Ubidots.

---

## 4. Menjalankan dan Memantau Data
- Jalankan server Flask
- Pastikan ESP32 terhubung dan mengirim data
- Periksa MongoDB untuk data yang tersimpan
- Pantau grafik pada dashboard Ubidots

---

## Kesimpulan
Dengan tutorial ini, Anda telah berhasil menghubungkan sensor DHT11 dan PIR ke ESP32, mengirim data ke MongoDB melalui server Flask, dan menampilkannya di dashboard Ubidots.

---

Semoga bermanfaat! 🚀

