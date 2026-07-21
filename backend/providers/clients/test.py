import httpx
import asyncio
import os

API_KEY = os.getenv("GOOGLE_API_KEY")

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": API_KEY},
        )
        print(r.json())

asyncio.run(main())