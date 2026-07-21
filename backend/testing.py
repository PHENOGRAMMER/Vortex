import asyncio
import httpx

async def main():

    async with httpx.AsyncClient(timeout=120) as client:

        r = await client.post(
            "http://localhost:11434/api/embed",
            json={
                "model":"bge-m3-b1024",
                "input":["hello"]
            }
        )

        print(r.status_code)
        print(r.text)

asyncio.run(main())