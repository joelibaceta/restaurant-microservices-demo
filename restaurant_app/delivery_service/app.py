from flask import Flask, request
import requests
import os


# Service Discovery with Consul
# ==========================================================

# Consul base URL, configurable via environment variable
CONSUL_BASE_URL = os.getenv("CONSUL_URL", "http://consul:8500")

def register_service():
    """
    Registers this service with Consul for service discovery.
    """
    service_definition = {
        "Name": "delivery",
        "Address": "delivery",
        "Port": 5002,
        "Check": {
            "HTTP": "http://delivery:5002/ping",
            "Interval": "10s"
        }
    }
    requests.put(f"{CONSUL_BASE_URL}/v1/agent/service/register", json=service_definition)

def discover_service(service_name):
    """
    Discovers a service by name using Consul.
    Returns the base URL of the discovered service.
    Raises an exception if the service is not found.
    """
    response = requests.get(f"{CONSUL_BASE_URL}/v1/catalog/service/{service_name}")
    data = response.json()
    if not data:
        raise Exception(f"Service '{service_name}' not found in Consul")
    address = data[0]["ServiceAddress"]
    port = data[0]["ServicePort"]
    return f"http://{address}:{port}"
# Register the delivery service with Consul on startup
register_service()

# Flask app section
# ==========================================================
# This section sets up the Flask application for the delivery service.


app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return {"message": "Delivery service is running"}, 200


@app.route("/deliver", methods=["POST"])
def deliver():
    data = request.get_json()
    print("🚚 Entregando orden a:", data.get("cliente"))
    return {"status": f"en camino a {data.get('cliente')}"}, 200

if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5002)