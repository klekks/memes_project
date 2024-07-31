import sqlalchemy.exc
from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy import select, delete


from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine("postgresql+asyncpg://postgres_user:postgres_password@db:5432/postgres_db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Memes(Base):
    __tablename__ = "Memes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(VARCHAR(length=256), nullable=False)
    filename = Column(VARCHAR(length=36), unique=True, nullable=False)
    mimetype = Column(VARCHAR(length=64), nullable=False)

    @staticmethod
    async def create_meme(filename, text, mimetype):
        meme = Memes(filename=filename, text=text, mimetype=mimetype)
        async with new_session() as session:
            session.add(meme)
            await session.commit()
            return {"id": meme.id, "mimetype": meme.mimetype, "text": meme.text}

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


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)