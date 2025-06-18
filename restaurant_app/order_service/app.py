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
        "Name": "order",
        "Address": "order",
        "Port": 5000,
        "Check": {
            "HTTP": "http://order:5000/ping",
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
# Register the order service with Consul on startup
register_service()


# Flask app section
# ==========================================================
# This section sets up the Flask application for the order service.

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    """
    Health check endpoint.
    """
    return {"message": "Order service is running"}, 200

@app.route("/order", methods=["POST"])
def create_order():
    """
    Receives an order and forwards it to the kitchen service.
    """
    data = request.get_json()
    print("📝 Order received:", data)

    try:
        kitchen_url = discover_service("kitchen")
        response = requests.post(f"{kitchen_url}/cook", json=data)
        return {
            "status": "sent to kitchen",
            "kitchen_response": response.json()
        }, 201
    except Exception as e:
        return {
            "error": "Could not contact kitchen service",
            "details": str(e)
        }, 500

if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5000)