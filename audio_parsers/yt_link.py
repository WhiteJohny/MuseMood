import yt_dlp
import os

LINK_PATTERN = 'https://www.youtube.com/watch?v='


def download_audio_as_wav(
        video_id: str,
        output_dir: str = ".",
):
    filename = os.path.join(output_dir, f'{video_id}.wav')
    if os.path.exists(filename):
        print(f'✅ Файл уже существует: {filename}')
        return True

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),
        'verbose': False,
        'socket_timeout': 5,
        # 'ffmpeg_location': 'C:\\Program Files\\FFmpeg\\bin'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(LINK_PATTERN + video_id, download=True)

            # Универсальная замена расширения
            base_name = os.path.splitext(ydl.prepare_filename(info))[0]
            filename = f"{base_name}.wav"

            if not os.path.exists(filename):
                raise FileNotFoundError(f"❌ Аудиофайл не найден: {filename}")

            print(f'✅ Скачано: {filename}')

            return True
    except Exception as e:
        print(f'❌ Ошибка: {str(e)}')
        return False


if __name__ == '__main__':
    from threading import Thread

    url_1 = "-0PcwE9DJRE"
    url_2 = "-07ZD2JpLvA"

    out_dir = "downloads"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    Thread(target=download_audio_as_wav, args=(url_1, out_dir)).start()
    Thread(target=download_audio_as_wav, args=(url_2, out_dir)).start()
