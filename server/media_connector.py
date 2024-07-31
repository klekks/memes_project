import httpx
import fastapi

from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

MEDIA_API_URL = "http://media:8081"

aclient = httpx.AsyncClient()


async def download_file(filename: str):
    api_url = f"{MEDIA_API_URL}/{filename}"
    request = aclient.build_request("GET", api_url)
    response = await aclient.send(request, stream=True)
    return StreamingResponse(response.aiter_raw(), background=BackgroundTask(response.aclose))


async def upload_file(file: fastapi.UploadFile):
    api_url = MEDIA_API_URL
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, files={'file': file.file})
        result = response.json()
        print(result)
        return result


async def delete_file(filename: str):
    api_url = f"{MEDIA_API_URL}/{filename}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(api_url)
        result = response.json()
        print(result)
        return result

