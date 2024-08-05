import httpx

MEDIA_API_URL = f"http://media:8081"  # TODO: env settings

aclient = httpx.AsyncClient()


async def download_file(filename: str):
    api_url = f"{MEDIA_API_URL}/{filename}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        result = response.json()

        return result['detail'][0]


async def upload_file(file):
    api_url = MEDIA_API_URL
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, files={'file': file.file})
        result = response.json()

        return result['detail'][0]


async def delete_file(filename: str) -> bool:
    api_url = f"{MEDIA_API_URL}/{filename}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(api_url)
        result = response.json()
        return result['detail'][0]['msg'] == "ok"


