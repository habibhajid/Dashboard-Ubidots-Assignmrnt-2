from machine import Pin
import dht
import network
import ujson
import utime
from umqtt.simple import MQTTClient

# Konstanta WiFi dan Ubidots
UBIDOTS_TOKEN = "BBUS-w4hoDRHaDcWGfZAO4RZITgVz6EoLhq"
WIFI_SSID = "MARGO ENJOY"
WIFI_PASS = "pesandulu"
DEVICE_LABEL = "esp32"
VAR_PIR = "pir_sensor"
VAR_TEMP = "temperature"

# Inisialisasi sensor dan koneksi
PIR_PIN = 27
DHT_PIN = 14

dht_sensor = dht.DHT22(Pin(DHT_PIN))
pir_sensor = Pin(PIR_PIN, Pin.IN)

# Koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        utime.sleep(1)
    print("Terhubung ke WiFi")

# Koneksi ke Ubidots
MQTT_BROKER = "industrial.api.ubidots.com"
MQTT_PORT = 1883
MQTT_TOPIC = b"/v1.6/devices/%s" % DEVICE_LABEL.encode()
MQTT_CLIENT_ID = "esp32"

client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT, user=UBIDOTS_TOKEN, password="")

def connect_mqtt():
    try:
        client.connect()
        print("Terhubung ke Ubidots MQTT")
    except Exception as e:
        print("Gagal koneksi ke MQTT:", str(e))

# Kirim data ke Ubidots
def send_data(pir_value, temperature):
    payload = ujson.dumps({
        VAR_PIR: {"value": pir_value},
        VAR_TEMP: {"value": temperature}
    })
    client.publish(MQTT_TOPIC, payload)
    print("Data terkirim:", payload)

# Program utama
def main():
    connect_wifi()
    connect_mqtt()
    while True:
        pir_value = pir_sensor.value()
        try:
            dht_sensor.measure()
            temperature = dht_sensor.temperature()
            send_data(pir_value, temperature)
        except Exception as e:
            print("Gagal membaca sensor:", str(e))
        utime.sleep(5)

if __name__ == "__main__":
    main()