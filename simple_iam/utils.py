import time
import hashlib

SECRET = "supersecreto"  # En producción usarías una variable de entorno

def generate_token(user_id, role):
    timestamp = str(int(time.time()))
    data = f"{user_id}:{role}:{timestamp}:{SECRET}"
    signature = hashlib.sha256(data.encode()).hexdigest()
    token = f"{user_id}:{role}:{timestamp}:{signature}"
    return token

def verify_token(token):
    try:
        user_id, role, timestamp, signature = token.split(":")
        expected = hashlib.sha256(f"{user_id}:{role}:{timestamp}:{SECRET}".encode()).hexdigest()
        if signature != expected:
            return None
        return {"sub": user_id, "role": role}
    except Exception:
        return None