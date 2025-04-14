import yt_dlp
import subprocess
import os


def download_audio_as_wav(
        url,
        output_dir: str = ".",
        start_time: int = None,
        end_time: int = None,
        counter: int = 1
):
    if start_time is not None and start_time < 0:
        raise ValueError("❌ start_time не может быть отрицательным")
    if end_time is not None and end_time < 0:
        raise ValueError("❌ end_time не может быть отрицательным")
    if start_time is not None and end_time is not None and start_time >= end_time:
        raise ValueError("❌ start_time должен быть меньше end_time")

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
            info = ydl.extract_info(url, download=True)

            # Универсальная замена расширения
            base_name = os.path.splitext(ydl.prepare_filename(info))[0]
            filename = f"{base_name}.wav"

            if not os.path.exists(filename):
                raise FileNotFoundError(f"❌ Аудиофайл не найден: {filename}")

            print(f'✅ Скачано: {filename}')

            # Обрезка аудио
            if start_time is not None or end_time is not None:
                temp_filename = f"{filename}_temp.wav"
                cmd = ['ffmpeg', '-y', '-i', filename]

                if start_time is not None:
                    cmd.extend(['-ss', str(start_time)])
                if end_time is not None:
                    cmd.extend(['-to', str(end_time)])

                cmd.extend(['-c', 'copy', temp_filename])

                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    os.replace(temp_filename, filename)
                    os.rename(filename, output_dir + f'/audio{counter}.wav')
                    print(f'✅ Обрезано: {filename}')
                except subprocess.CalledProcessError as e:
                    print(f'❌ Ошибка обрезки: {e.stderr.decode()}')
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    return None
            return filename
    except Exception as e:
        print(f'❌ Ошибка: {str(e)}')
        os.chdir(output_dir)
        with open(f'audio{counter}_error.wav', 'w+'):
            print(f'Создан файл заглушка - audio{counter}_error.wav')
        os.chdir(f'..')
        return None


# Пример использования
# url_1 = "https://www.youtube.com/watch?v=-0PcwE9DJRE"
# url_2 = "https://www.youtube.com/watch?v=-07ZD2JpLvA"
# download_audio_as_wav(
#     url_1,
#     output_dir="downloads",
#     start_time=10,
#     end_time=20
# )
