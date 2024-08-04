import sqlalchemy.exc
from sqlalchemy import Column, Integer, VARCHAR, Text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from settings import database_settings, service_settings


class AsyncDeclarativeBase(AsyncAttrs, DeclarativeBase):
    pass


postgres_url = "postgresql+asyncpg://{0}:{1}@db:{2}/{3}".format(database_settings.POSTGRES_USER,
                                                                database_settings.POSTGRES_PASSWORD,
                                                                database_settings.POSTGRES_PORT,
                                                                database_settings.POSTGRES_DB)

engine = create_async_engine(postgres_url)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Memes(AsyncDeclarativeBase):
    __tablename__ = service_settings.DB_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(VARCHAR(length=service_settings.MAX_MEMES_TEXT_LENGTH), nullable=False)
    filename = Column(VARCHAR(length=service_settings.MAX_FILE_NAME_LENGTH), unique=True, nullable=False)
    old_name = Column(Text, nullable=False)
    mimetype = Column(VARCHAR(length=64), nullable=False)

    @staticmethod
    async def create_meme(old_name, filename, text, mimetype):
        meme = Memes(old_name=old_name, filename=filename, text=text, mimetype=mimetype)
        async with new_session() as session:
            session.add(meme)
            await session.commit()
            return {"id": meme.id, "text": meme.text}

    @staticmethod
    async def _get_meme(query):
        async with new_session() as session:
            result = await session.execute(query)
            try:
                meme = result.scalars().one()
            except sqlalchemy.exc.NoResultFound:
                meme = None
            return meme

    @staticmethod
    async def delete_by_id(ident) -> bool:
        async with new_session() as session:
            try:
                memes = await session.get(Memes, ident)
                await session.delete(memes)
                await session.commit()
                return True
            except:
                return False

    @staticmethod
    async def get_meme_by_id(ident):
        return await Memes._get_meme(select(Memes).filter(Memes.id == ident))

    @staticmethod
    async def get_meme_by_filename(filename):
        return await Memes._get_meme(select(Memes).filter(Memes.filename == filename))

    @staticmethod
    async def get_memes(offset, limit):
        query = select(Memes).offset(offset).limit(limit)
        async with new_session() as session:
            result = await session.execute(query)
            memes = result.scalars().all()
            return memes

    async def update(self, **kwargs):
        query = update(Memes).filter(Memes.id == self.id).values(**kwargs)
        async with new_session() as session:
            memes = await session.execute(query)
            await session.commit()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(AsyncDeclarativeBase.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(AsyncDeclarativeBase.metadata.drop_all)
