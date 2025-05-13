from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, relationship

from src.bot.logic.settings import Secrets

Base = declarative_base()

playlists_audios = Table(
    'playlists_audios',
    Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id', ondelete='CASCADE'), primary_key=True),
    Column('audio_id', Integer, ForeignKey('audios.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    premium = Column(Boolean)

    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")


class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = relationship("User", back_populates="playlists")
    audios = relationship("Audio", secondary=playlists_audios, lazy="selectin", back_populates="playlists")

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_id_name'),
    )


class Audio(Base):
    __tablename__ = 'audios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    sentiment = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    file_id = Column(String)
    link = Column(String)

    playlists = relationship("Playlist", secondary=playlists_audios, lazy="selectin", back_populates="audios")


DATABASE_URL = f'postgresql+asyncpg://{Secrets.db_user}:{Secrets.db_password}@{Secrets.db_host}:{Secrets.db_port}/{Secrets.db_name}'
engine = create_async_engine(DATABASE_URL)
async_session_local = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
