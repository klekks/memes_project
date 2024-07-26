import uuid
from os import path

from fastapi import FastAPI, UploadFile, HTTPException
from contextlib import asynccontextmanager
from model import Memes, create_tables, delete_tables


def random_name() -> str:
    return str(uuid.uuid4())


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_tables()
    yield
    await delete_tables()


app = FastAPI(lifespan=lifespan)


@app.post("/{path:path}")
async def create_upload_file(filepath: str, file: UploadFile):
    file.filename = path.join(filepath, random_name())
    try:
        return await Memes.create_meme(file)
    except Exception as e:
        print(e)
        raise HTTPException(503, "Media file was not uploaded")


@app.get("/{filename:path}")
async def create_upload_file(filename: str):
    try:
        return await Memes.get_meme(filename)
    except Exception as e:
        print(e)
        raise HTTPException(404, "Media file not found")
