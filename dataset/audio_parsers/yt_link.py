import yt_dlp
import subprocess
import os


def download_audio_as_wav(url, output_dir=".", start_time=None, end_time=None):
    # Валидация параметров времени
    if start_time is not None and start_time < 0:
        raise ValueError("❌ start_time не может быть отрицательным")
    if end_time is not None and end_time < 0:
        raise ValueError("❌ end_time не может быть отрицательным")
    if start_time is not None and end_time is not None and start_time >= end_time:
        raise ValueError("❌ start_time должен быть меньше end_time")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'verbose': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(output_dir, f"{info['title']}.wav")
            print(f'✅ Скачано: {filename}')

            # Обрезка аудио, если указаны временные границы
            if start_time is not None or end_time is not None:
                temp_filename = f"{filename}_temp.wav"
                cmd = ['ffmpeg', '-y']  # -y для перезаписи файла без подтверждения

                if start_time is not None:
                    cmd.extend(['-ss', str(start_time)])
                if end_time is not None:
                    cmd.extend(['-to', str(end_time)])

                cmd.extend(['-i', filename, '-c', 'copy', temp_filename])

                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    os.replace(temp_filename, filename)
                    print(f'✅ Обрезано: {filename}')
                except subprocess.CalledProcessError as e:
                    print(f'❌ Ошибка обрезки: {e.stderr.decode()}')
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    return None
                except Exception as e:
                    print(f'❌ Ошибка при обрезке: {str(e)}')
                    return None

            return filename
    except Exception as e:
        print(f'❌ Ошибка скачивания: {str(e)}')
        return None


# Пример использования
# download_audio_as_wav(
#     "https://youtu.be/dQw4w9WgXcQ",
#     output_dir="downloads",
#     start_time=100,
#     end_time=120
# )
