import asyncio

import yt_dlp
import os

from src.bot.logic.settings import bot, logger, set_log
from src.bot.logic.utils.audio_converters import convert_to_wav

OUTPUT_DIR = "temp"
MAX_SIZE = 10 * 1024 * 1024  # 10 МБ


async def download_tg_audio(message, bot=bot, output_dir: str = OUTPUT_DIR):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    try:
        if message.audio.file_size > MAX_SIZE:
            return await message.answer("Файл слишком большой!")

        audio_id = message.audio.file_id
        audio = await bot.get_file(audio_id)
        audio_path = audio.file_path
        download_path = os.path.join(output_dir, f'{message.audio.file_name}.wav')
        await bot.download_file(audio_path, os.path.join(output_dir, message.audio.file_name))
        await asyncio.to_thread(
            convert_to_wav,
            os.path.join(output_dir, message.audio.file_name),
            download_path
        )

        if not os.path.isfile(download_path):
            raise FileNotFoundError(f"Audio not found: {download_path}")

        return download_path
    except Exception as e:
        logger.info(set_log('Download audio TG', special=f'Error: {e}'))
        return None


def download_yt_audio(url: str, output_dir: str = OUTPUT_DIR):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'verbose': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration') or 0
            file_size = info.get('filesize') or MAX_SIZE + 1
            if file_size > MAX_SIZE:
                raise ValueError('Audiofile size too big')

            info = ydl.extract_info(url, download=True)

            base_name = os.path.splitext(ydl.prepare_filename(info))[0]
            filename = f"{output_dir}/{base_name}.wav"

            if not os.path.exists(filename):
                raise FileNotFoundError(f"Audiofile not found: {filename}")

            return filename, duration
    except Exception as e:
        logger.info(set_log('Download audio YT', special=f'Error: {e}'))
        return None, None
