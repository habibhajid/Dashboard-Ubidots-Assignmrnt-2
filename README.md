# Lintas Alam IoT Dashboard

Proyek ini bertujuan untuk membuat dashboard di Ubidots dengan minimal 4 visualisasi, mengirimkan data sensor dari ESP32 ke Ubidots melalui REST API/MQTT, serta menyimpan data sensor ke MongoDB menggunakan Flask API.

---

## 🚀 Fitur
- Menggunakan minimal 2 sensor untuk pengambilan data.
- Mengirim data ke Ubidots melalui REST API/MQTT.
- Menyimpan data sensor ke MongoDB melalui API Flask.
- Menampilkan data sensor di dashboard Ubidots dengan minimal 4 visualisasi (grafik, gauge, dll).

---

## 📜 Persyaratan
- ESP32 (dengan sensor PIR dan DHT22 dalam contoh ini).
- Ubidots untuk dashboard.
- Flask & MongoDB untuk API backend.
- Koneksi WiFi.
- Laptop dengan Python terinstal.

---

## 1. Wiring ESP32 dengan Sensor

Berikut adalah skema koneksi:
- **DHT11/DHT22**:
  - VCC ke **3.3V** ESP32
  - GND ke **GND** ESP32
  - Data ke **GPIO14**
- **PIR Sensor**:
  - VCC ke **3.3V** ESP32
  - GND ke **GND** ESP32
  - Output ke **GPIO27**

Pastikan semua koneksi sudah sesuai sebelum melanjutkan ke tahap pemrograman.

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
client = MongoClient("mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.mongodb.net/?retryWrites=true&w=majority")
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

### 2.3 ESP32: Mengirim Data Sensor

#### a. Library yang diperlukan di ESP32:
Pastikan ESP32 memiliki MicroPython dan pustaka berikut:
- `urequests` untuk HTTP request ke API.
- `dht` untuk membaca sensor suhu & kelembaban.
- `network` untuk koneksi WiFi.
- `machine` untuk membaca input dari sensor PIR.

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
FLASK_URL = "http://<SERVER_IP>:5000/sensor"

# Fungsi Koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Menghubungkan ke WiFi...")
    while not wlan.isconnected():
        utime.sleep(1)
    
    print("Terhubung ke WiFi:", wlan.ifconfig())

# Fungsi untuk Membaca Sensor
def read_sensors():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        pir_value = pir_sensor.value()
    except Exception as e:
        print("Gagal membaca sensor:", str(e))
        temperature, humidity, pir_value = -1, -1, -1
    
    return temperature, humidity, pir_value

# Fungsi Kirim Data ke Flask API
def send_data():
    while True:
        temperature, humidity, pir_value = read_sensors()
        payload = {"temperature": temperature, "humidity": humidity, "pir_sensor": pir_value}
        
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
4. Gunakan **Webhook** untuk menghubungkan Flask API ke Ubidots.

Cara menggunakan Webhook di Ubidots:
- Masuk ke **Plugins** > **Add Plugin** > **Webhook**.
- Tambahkan endpoint **http://<SERVER_IP>:5000/sensor** dengan metode **POST**.
- Atur format data sesuai dengan payload ESP32.

---

## 4. Menjalankan dan Memantau Data
- Jalankan server Flask dengan `python server.py`.
- Pastikan ESP32 terhubung dan mengirim data.
- Periksa MongoDB untuk data yang tersimpan.
- Pantau grafik pada dashboard Ubidots.

---

## Kesimpulan
Dengan tutorial ini, Anda telah berhasil menghubungkan sensor DHT11 dan PIR ke ESP32, mengirim data ke MongoDB melalui server Flask, serta menampilkannya di dashboard Ubidots.

Semoga bermanfaat! 🚀

