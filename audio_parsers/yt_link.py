import yt_dlp

def download_audio_as_wav(url, output_dir="."):
    # Настройки для yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',           # Выбрать лучший аудиопоток
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',      # Использовать FFmpeg для извлечения аудио
            'preferredcodec': 'wav',          # Указать формат WAV
            'preferredquality': '192',        # Качество (не влияет на WAV, но параметр обязателен)
        }],
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',  # Шаблон имени файла
        'verbose': False                      # Отключить логи (если нужно — поменяйте на True)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f'✅ Скачано: {info["title"]}.wav')
            return f'{output_dir}/{info["title"]}.wav'
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return None

# Пример использования
download_audio_as_wav("https://youtu.be/dQw4w9WgXcQ", output_dir="downloads")