import os
import subprocess

FFMPEG_LOCATION = 'C:/Program Files/FFmpeg/bin/ffmpeg.exe'


def crop_audio(
        filename: str,
        start_time: int,
        end_time: int,
        out_filename: str
):
    if start_time >= end_time:
        raise ValueError("❌ start_time должен быть меньше end_time")

    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ Файл {filename} не найден")

    if os.path.exists(out_filename):
        print(f'✅ Файл уже существует: {out_filename}')
        return True

    cmd = [
        FFMPEG_LOCATION, '-y', '-i', filename,
        '-ss', str(start_time),
        '-to', str(end_time),
        '-c', 'copy', out_filename
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f'✅ Обрезано: {out_filename}')
    except subprocess.CalledProcessError as e:
        print(f'❌ Ошибка обрезки: {e.stderr.decode()}')
        if os.path.exists(out_filename):
            os.remove(out_filename)
        return False

    return True


def split_audio(
        filename: str,
        output_dir: str
):
    """Разделяет аудио на сегменты по 10 секунд"""
    raise NotImplementedError
