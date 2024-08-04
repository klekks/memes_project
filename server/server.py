from fastapi import FastAPI, Query, UploadFile, HTTPException
from contextlib import asynccontextmanager

from model import Memes, create_tables, delete_tables
from media_connector import upload_file, delete_file, download_file

from responses import MemesInfo, MemesFullInfo

from validators import image_validator, valid_memes, image_validation_func
from settings import service_settings

ALLOWED_IMAGE_TYPES = set(service_settings.ALLOWED_IMAGE_TYPES.split(','))
IMAGE_MAX_SIZE = service_settings.MAX_IMAGE_SIZE


@asynccontextmanager
async def dev_lifespan(fap: FastAPI):
    await create_tables()
    yield
    await delete_tables()


app = FastAPI(lifespan=dev_lifespan)


@app.get("/memes")
async def get_memes(offset: int = Query(0, ge=0, title="Number of items will be skipped"),
                    limit: int = Query(10, ge=1, le=service_settings.PAGINATION_MAX_PER_PAGE,
                                       title="Number of items on the page")):
    return await Memes.get_memes(offset, limit)


# TODO: await download_file returns json with {"url" : "url"} to direct download
@app.get("/memes/{memes_id}", response_model=MemesFullInfo)
async def get_meme_by_id(memes: Memes = valid_memes):
    memes_info = await download_file(memes.filename)
    del memes.filename
    memes.url = memes_info['url']
    return memes


@app.post("/memes", response_model=MemesInfo)
async def add_new_meme(file: image_validator,
                       text: str = Query(min_length=1,
                                         max_length=service_settings.MAX_MEMES_TEXT_LENGTH,
                                         description="Description of the meme. It will be attached to the image.")):
    upload_result = await upload_file(file)

    if "file_name" in upload_result:
        filename = upload_result["file_name"]
    else:
        raise HTTPException(status_code=500, detail="Error while loading image on storage")

    return await Memes.create_meme(file.filename, filename, text, file.content_type)


@app.delete("/memes/{memes_id}", response_model=MemesInfo)
async def delete_memes(memes: Memes = valid_memes):
    is_deleted = await Memes.delete_by_id(memes.id)

    if is_deleted:
        await delete_file(memes.filename)
        return memes

    raise HTTPException(status_code=500, detail="Error while deleting memes")


@app.put("/memes/{memes_id}", response_model=MemesInfo)
async def update_memes(file: UploadFile = None,
                       memes: Memes = valid_memes,
                       new_text: str = Query(None, min_length=1, max_length=256, title="Description of the meme")):

    if new_text is not None and memes.text != new_text:
        await memes.update(text=new_text)

    if file is not None:
        image_validation_func(file)
        upload_result = await upload_file(file)
        await memes.update(filename=upload_result['file_name'])

    return await Memes.get_meme_by_id(memes.id)
