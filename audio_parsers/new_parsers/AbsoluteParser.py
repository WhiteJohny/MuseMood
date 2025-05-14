import yt_dlp
from yandex_music import Client
from vk_api import VkApi
import os


class AudioDownloader:
    def __init__(self, services_config):
        self.services = {
            'youtube': self.download_youtube,
            'yandex': self.download_yandex,
            'vk': self.download_vk
        }

        # Конфигурация для сервисов
        self.yandex_client = Client(token=services_config.get('yandex_token'))
        self.vk_session = VkApi(token=services_config.get('vk_token'))

    def download_audio(self, service: str, track_id: str, output_dir: str = "."):
        if service not in self.services:
            raise ValueError(f"Unsupported service: {service}")

        return self.services[service](track_id, output_dir)

    # Существующая YouTube реализация
    def download_youtube(self, video_id: str, output_dir: str):
        pass

    # Яндекс.Музыка (концепт)
    def download_yandex(self, track_id: str, output_dir: str):
        try:
            track = self.yandex_client.tracks(track_id)[0]
            filename = os.path.join(output_dir, f'{track_id}.wav')

            if os.path.exists(filename):
                print(f'✅ Файл уже существует: {filename}')
                return True

            download_info = track.get_download_info(get_direct_links=True)
            best_link = max(
                [d for d in download_info if d.codec == 'wav'],
                key=lambda d: d.bitrate_in_kbps
            )

            ydl_opts = {
                'outtmpl': filename,
                'verbose': False,
                'socket_timeout': 5
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([best_link.direct_link])

            print(f'✅ Скачано: {filename}')
            return True
        except Exception as e:
            print(f'❌ Ошибка Яндекс.Музыка: {str(e)}')
            return False

    # VK Music (концепт)
    def download_vk(self, audio_id: str, output_dir: str):
        try:
            filename = os.path.join(output_dir, f'{audio_id}.wav')

            if os.path.exists(filename):
                print(f'✅ Файл уже существует: {filename}')
                return True

            # Получение информации о треке
            audio = self.vk_session.method('audio.getById', {'audios': audio_id})[0]

            # Использование прямой ссылки на аудио
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'outtmpl': os.path.join(output_dir, f'{audio_id}.%(ext)s'),
                'verbose': False,
                'socket_timeout': 5
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([audio['url']])

            print(f'✅ Скачано: {filename}')
            return True
        except Exception as e:
            print(f'❌ Ошибка VK: {str(e)}')
            return False


if __name__ == '__main__':
    config = {
        'yandex_token': 'ВАШ_ТОКЕН',
        'vk_token': 'ВАШ_ТОКЕН'
    }

    downloader = AudioDownloader(config)

    # Пример использования
    downloader.download_audio('youtube', '-0PcwE9DJRE', 'downloads')
    downloader.download_audio('yandex', 'track_id_пример', 'downloads')
    downloader.download_audio('vk', 'audio_id_пример', 'downloads')