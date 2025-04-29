import os
import pandas as pd

from audio_converter import extract_mood_features


def make_dataset(audio_dir: str, file_name: str, data: pd.DataFrame) -> bool:
    if not os.path.isdir(audio_dir):
        print("Неправильный путь до директории!")
        return False

    audios = []
    dataset = []
    files = os.listdir(audio_dir)

    for file in files:
        if file.endswith('.wav'):
            audios.append(file)

    if len(audios) != len(data):
        print("Количество аудиофайлов неравно размеру датасета!")
        return False

    for i in range(len(audios)):
        audio = audios[i]
        if audio.endswith('_error.wav'):
            continue

        frame = data.iloc[i]
        try:
            dataset.append(
                [
                    extract_mood_features(audio_dir + '/' + audio),
                    frame['start_seconds'],
                    frame['end_seconds'],
                    frame['funny'],
                    frame['happy'],
                    frame['sad'],
                    frame['scary'],
                    frame['tender'],
                    frame['trance']
                ]
            )
        except Exception as e:
            print('неправильно сформированные данные!', e)
            return False

    dataset = pd.DataFrame(
        dataset,
        columns=[
            'features',
            'start_seconds',
            'end_seconds',
            'funny',
            'happy',
            'sad',
            'scary',
            'tender',
            'trance'
        ]
    )

    dataset.to_csv(
        file_name,
        sep=',',
        index=False,
        encoding='utf-8'
    )

    return True
