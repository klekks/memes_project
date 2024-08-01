from fastapi import FastAPI, Query, UploadFile, HTTPException, Header, Depends
from contextlib import asynccontextmanager

from model import Memes, create_tables, delete_tables


from media_connector import upload_file, delete_file, download_file


ALLOWED_IMAGE_TYPES = {"png", "jpeg", "gif", "apng", "webp"}
IMAGE_MAX_SIZE = 8 * 1024 * 1024  # 8MB


@asynccontextmanager
async def dev_lifespan(fap: FastAPI):
    await create_tables()
    yield
    await delete_tables()


app = FastAPI(lifespan=dev_lifespan)


@app.get("/memes")
async def get_memes(offset: int = Query(0, ge=0, title="Number of items will be skipped"),
                    limit: int = Query(10, ge=1, le=50, title="Number of items on the page")):
    return await Memes.get_memes(offset, limit)


@app.get("/memes/{id}")
async def get_meme_by_id(id: int):
    meme_info = await Memes.get_meme_by_id(id)
    if meme_info is None:
        raise HTTPException(status_code=404, detail="Memes not found.")

    meme_image = await download_file(meme_info.filename)
    meme_image.headers['Content-Type'] = meme_info.mimetype
    meme_image.headers['Text'] = meme_info.text
    return meme_image


@app.post("/memes")
async def add_new_meme(file: UploadFile,
                       text: str = Query(min_length=1, max_length=256, title="Description of the meme")
                       ):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="You can only pin an image to memes")

    if not file.content_type[6:] in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Image format is not supported")

    if file.size > IMAGE_MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"Image size should be at most 8MB, your image is {file.size // 1024} KB")

    upload_result = dict(await upload_file(file))
    if "file_name" in upload_result:
        filename = upload_result["file_name"]
    else:
        raise HTTPException(status_code=500, detail="Error while loading image on storage")

    return await Memes.create_meme(filename, text, file.content_type)


@app.delete("/memes/{id}")
async def delete_memes(id: int):

    meme_info = await Memes.get_meme_by_id(id)
    if meme_info is None:
        raise HTTPException(status_code=404, detail="Memes not found.")

    is_deleted = await Memes.delete_by_id(id)

    if is_deleted:
        return await delete_file(meme_info.filename)

    raise HTTPException(status_code=500, detail="Error while deleting memes")
