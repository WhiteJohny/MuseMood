from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import User, Playlist, Audio


# Users
async def create_user(session: AsyncSession, user_id: int, username: str, premium: bool = None):
    user = User(id=user_id, username=username, premium=premium)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int):
    result = await session.get(User, user_id)
    return result


async def update_user(session: AsyncSession, user_id: int, new_username: str = None, new_premium: bool = None):
    user = await session.get(User, user_id)
    if not user:
        return None

    if new_username:
        user.username = new_username
    if new_premium is not None:
        user.premium = new_premium

    await session.commit()
    return user


async def delete_user(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True


# Playlists
async def create_playlist(session: AsyncSession, name: str, user_id: int):
    playlist = Playlist(name=name, user_id=user_id)
    session.add(playlist)
    await session.commit()
    await session.refresh(playlist)
    return playlist


async def get_user_playlists(session: AsyncSession, user_id: int):
    stmt = select(
        Playlist.id,
        Playlist.name
    ).where(
        Playlist.user_id == user_id
    )
    result = await session.execute(stmt)
    return result.all()


async def get_user_playlist(session: AsyncSession, user_id: int, name: str = 'All'):
    stmt = select(
        Playlist.id,
    ).where(
        (Playlist.user_id == user_id) &
        (Playlist.name == name)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_playlist_title(session: AsyncSession, playlist_id: int):
    stmt = select(
        Playlist.name
    ).where(
        Playlist.id == playlist_id
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def add_audio_to_playlist(session: AsyncSession, playlist_id: int, audio_id: int):
    playlist = await session.get(Playlist, playlist_id)
    audio = await session.get(Audio, audio_id)

    if not playlist or not audio:
        return False

    await session.run_sync(
        lambda sync_session: playlist.audios.append(audio)
    )
    await session.commit()
    return True


async def remove_audio_from_playlist(session: AsyncSession, playlist_id: int, audio_id: int):
    playlist = await session.get(Playlist, playlist_id)
    audio = await session.get(Audio, audio_id)

    if not playlist or not audio:
        return False

    try:
        playlist.audios.remove(audio)
        await session.commit()
        return True
    except ValueError:
        return False


# Audios
async def create_audio(
        session: AsyncSession,
        title: str, message_id: int,
        sentiments: int = None,
        file_id: str = None,
        link: str = None
) -> Audio:
    audio = Audio(title=title, message_id=message_id, sentiments=sentiments, file_id=file_id, link=link)
    session.add(audio)
    await session.commit()
    await session.refresh(audio)
    return audio


async def get_audio(session: AsyncSession, audio_id: int):
    return await session.get(Audio, audio_id)


async def get_audio_by_link(session: AsyncSession, link: str):
    stmt = select(
        Audio.id
    ).where(
        Audio.link == link or Audio.path == link
    )
    result = await session.execute(stmt)
    return result.all()


async def get_audios_in_playlist(session: AsyncSession, playlist_id: int):
    playlist = await session.get(Playlist, playlist_id, options=[selectinload(Playlist.audios)])
    return playlist.audios if playlist else []


async def remove_audio(session: AsyncSession, audio_id: int):
    audio = await session.get(Audio, audio_id)

    if not audio:
        return False

    await session.delete(audio)
    await session.commit()

    return True
