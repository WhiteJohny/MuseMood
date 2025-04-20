import os
import pandas as pd
from queue import Queue
from threading import Thread
from audio_parsers.mood_features import extract_mood_features


def worker(audio_dir: str, input_queue: Queue, return_queue: Queue):
    while True:
        args = input_queue.get()
        if args is None:
            return_queue.put(None)
            break

        video_id, start_seconds, end_seconds, i = args

        audio_path = os.path.join(audio_dir, f"{video_id},{start_seconds},{end_seconds}.wav")

        if not os.path.exists(audio_path):
            print(f'{i}: Аудио {audio_path} не найдено, запись будет пропущена')
            continue

        print(f'{i}: Извлечение признаков аудио {audio_path}')
        try:
            res = extract_mood_features(audio_path)
            return_queue.put((i, res))
        except Exception as e:
            print(f'{i}: Неправильно сформированные данные!', e)


def make_dataset(filename: str, audio_dir: str, output_dir: str, workers: int = 1) -> bool:
    if not os.path.exists(filename):
        raise FileNotFoundError(f'{filename} не найден')

    data = pd.read_csv(filename)
    features = {}
    dataset = []

    input_queue = Queue()
    return_queue = Queue()
    for _ in range(workers):
        Thread(target=worker, args=(audio_dir, input_queue, return_queue), daemon=True).start()

    # Send audio info to workers
    print('Отправка задач по потокам...')
    for i in range(len(data)):
        frame = data.iloc[i]
        input_queue.put((
            frame['YTID'],
            frame['start_seconds'],
            frame['end_seconds'],
            i
        ))

    # Send stop signal
    for _ in range(workers):
        input_queue.put(None)

    print('Ожидание потоков...')
    # Wait for workers to finish
    count_workers_done = 0
    while True:
        res = return_queue.get()
        if res is None:
            count_workers_done += 1
            if count_workers_done == workers: break
            else: continue

        i, res = res

        features[i] = res

    # Combine features with mood results
    print('Объединение признаков с эмоциональными оценками...')
    for i in range(len(data)):
        if i not in features: continue

        frame = data.iloc[i]

        dataset.append([
            features[i],
            frame['funny'],
            frame['happy'],
            frame['sad'],
            frame['scary'],
            frame['tender'],
            frame['trance']
        ])

    pd.DataFrame(
        dataset,
        columns=[
            'features',
            'funny',
            'happy',
            'sad',
            'scary',
            'tender',
            'trance'
        ]
    ).to_csv(
        os.path.join(output_dir, os.path.basename(filename)),
        sep=',',
        index=False,
        encoding='utf-8'
    )

    return True


def main():
    audio_dir = 'data/audio/cropped'
    if not os.path.exists(audio_dir):
        raise FileNotFoundError(f'Директория {audio_dir} не найдена')

    dataset_dir = 'data/preprocessed'
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f'Директория {dataset_dir} не найдена')

    output_dir = 'data/processed'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    workers = 20

    make_dataset(os.path.join(dataset_dir, 'eval_segments.csv'), audio_dir, output_dir, workers)
    # make_dataset(os.path.join(dataset_dir, 'balanced_train_segments.csv'), audio_dir, output_dir, workers)
    # make_dataset(os.path.join(dataset_dir, 'unbalanced_train_segments.csv'), audio_dir, output_dir, workers)


if __name__ == '__main__':
    main()
