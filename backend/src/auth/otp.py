import secrets
from src.auth.redis_client import redis_client


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


async def save_otp(email: str, otp: str):
    await redis_client.set(f"otp:{email}", ex=300, value=otp)


async def verify_otp(email: str, otp: str) -> bool:
    stored_otp = await redis_client.get(f"otp:{email}")
    if stored_otp and stored_otp == otp:
        await redis_client.delete(f"otp:{email}")
        return True
    return False
