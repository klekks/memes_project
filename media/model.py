from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import select
from storage import PublicAssetS3Storage


from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine("sqlite+aiosqlite:///test.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Memes(Base):
    __tablename__ = "Memes"

    id = Column(Integer, primary_key=True)
    file = Column(FileType(storage=PublicAssetS3Storage()))

    @staticmethod
    async def create_meme(file):
        meme = Memes(file=file)
        async with new_session() as session:
            session.add(meme)
            await session.commit()
            return {"name": meme.file.filename, "size": file.size}

    @staticmethod
    async def get_meme(filename):
        query = select(Memes)
        async with new_session() as session:
            result = await session.execute(query)
            file = result.scalars().all()
            return file


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
