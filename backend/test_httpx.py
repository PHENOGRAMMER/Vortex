import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:11434/api/tags")
        print(r.status_code)
        print(r.text)

asyncio.run(main())