class Token:
    def __init__(self, role: str):
        self.role = role
        self.random_id = 0

    def encode() -> str:
        return ""
    
    @classmethod
    def from_str(cls, token: str) -> 'Token':
        return Token("deb")
