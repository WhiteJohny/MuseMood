import os

from tempfile import TemporaryDirectory
from unittest.mock import patch

from audio_parsers.yt_link import download_audio_as_wav


def test_successful_download():
    with TemporaryDirectory() as tmp_dir:
        video_id = "dQw4w9WgXcQ"
        result = download_audio_as_wav(video_id, tmp_dir)
        output_file = os.path.join(tmp_dir, f"{video_id}.wav")

        assert result is True
        assert os.path.exists(output_file)


def test_existing_file():
    with TemporaryDirectory() as tmp_dir:
        video_id = "-07ZD2JpLvA"
        existing_file = os.path.join(tmp_dir, f"{video_id}.wav")
        open(existing_file, "w").close()  # Создаем пустой файл

        result = download_audio_as_wav(video_id, tmp_dir)

        assert result is True
        assert os.path.getsize(existing_file) == 0  # Файл не перезаписан


def test_invalid_video_id():
    with TemporaryDirectory() as tmp_dir:
        video_id = "invalid_id_123"
        result = download_audio_as_wav(video_id, tmp_dir)

        assert result is False


def test_output_dir_creation():
    with TemporaryDirectory() as tmp_dir:
        new_dir = os.path.join(tmp_dir, "new_folder")
        video_id = "dQw4w9WgXcQ"

        result = download_audio_as_wav(video_id, new_dir)
        output_file = os.path.join(new_dir, f"{video_id}.wav")

        assert result is True
        assert os.path.exists(new_dir)
        assert os.path.exists(output_file)


def test_output_format():
    with TemporaryDirectory() as tmp_dir:
        video_id = "dQw4w9WgXcQ"
        download_audio_as_wav(video_id, tmp_dir)
        output_file = os.path.join(tmp_dir, f"{video_id}.wav")

        # Проверка сигнатуры файла (пример для WAV)
        with open(output_file, "rb") as f:
            header = f.read(4)
            assert header == b"RIFF"  # Сигнатура WAV-файла


def test_network_error():
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_instance = mock_ydl.return_value.__enter__.return_value
        mock_instance.extract_info.side_effect = Exception("Network error")

        result = download_audio_as_wav("test_id")
        assert result is False