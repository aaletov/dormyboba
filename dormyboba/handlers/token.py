import base64
import jwt
from ..config import PRIVATE_KEY
from .random import random_id

class Token:
    def __init__(self):
        self.role = ""
        self.random_id = 0

    def __init__(self, role: str):
        self.role = role
        self.random_id = random_id()

    def encode(self) -> str:
        once_encoded = jwt.encode({
            "role": self.role,
            "random_id": self.random_id,
        }, key=PRIVATE_KEY, algorithm="RS256")

        return base64.b64encode(once_encoded.encode("utf-8")).decode("utf-8")
    
    @classmethod
    def from_str(cls, token: str) -> 'Token':
        once_encoded = base64.b64decode(token.encode("utf-8"))
        decoded = jwt.decode(once_encoded, key=PRIVATE_KEY, algorithms=["RS256"])
        token = Token()
        token.role = decoded["role"]
        token.random_id = decoded["random_id"]
        return token
