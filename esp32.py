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
