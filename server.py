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
