from flask import Flask, request, jsonify
from utils import generate_token, verify_token

import requests
import os


def register_service():
    consul_host = os.environ.get("CONSUL_HOST", "http://localhost:8500")
    service_definition = {
        "Name": "simple_iam",
        "Address": "simple_iam",  # nombre del servicio en docker-compose
        "Port": 5003,
        "Check": {
            "HTTP": "http://simple_iam:5003/ping",
            "Interval": "10s"
        }
    }
    try:
        r = requests.put(f"{consul_host}/v1/agent/service/register", json=service_definition)
        print("✅ Registrado en Consul:", r.status_code)
    except Exception as e:
        print("❌ Error al registrar en Consul:", e)


app = Flask(__name__)

# Demo: credenciales hardcodeadas
users_db = {
    "joel": {"password": "1234", "role": "admin"},
    "ana": {"password": "abcd", "role": "kitchen"},
}

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "IAM service is running"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = data.get("username")
    pwd = data.get("password")

    user_data = users_db.get(user)
    if not user_data or user_data["password"] != pwd:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user, user_data["role"])
    return jsonify({"token": token})

@app.route("/validate", methods=["GET"])
def validate():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid token"}), 401

    # Headers que NGINX puede propagar
    return jsonify({
        "x-user-id": payload["sub"],
        "x-role": payload["role"]
    }), 200

if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5003)