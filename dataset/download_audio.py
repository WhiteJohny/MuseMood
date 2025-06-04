import os
import pandas as pd
from threading import Thread
from queue import Queue
from audio_parsers.yt_link import download_audio_as_wav
from audio_parsers.split_audio import crop_audio


def crop_worker(crop_queue: Queue, output_dir: str):
    while True:
        args = crop_queue.get()
        if args is None:
            crop_queue.task_done()
            return

        try:
            video_id, start_seconds, end_seconds, filename = args
            crop_audio(
                filename,
                start_seconds,
                end_seconds,
                os.path.join(output_dir, f'{video_id},{start_seconds},{end_seconds}.wav')
            )
        except Exception as e:
            print(f'Ошибка при скачивании аудио: {e}')
        crop_queue.task_done()


def download_worker(download_queue: Queue, crop_queue: Queue, output_dir: str):
    while True:
        args = download_queue.get()
        if args is None:
            download_queue.task_done()
            return

        video_id, start_seconds, end_seconds, i = args

        try:
            if download_audio_as_wav(video_id, output_dir):
                print(f'{i}: Аудио успешно скачано')
                crop_queue.put((
                    video_id,
                    start_seconds,
                    end_seconds,
                    os.path.join(output_dir, f'{video_id}.wav')
                ))
        except Exception as e:
            print(f'{i}: Ошибка при скачивании аудио: {e}')
        download_queue.task_done()


def download_audio(
        filename: str,
        download_dir: str,
        crop_dir: str,
        download_workers: int = 1,
        crop_workers: int = 1
):
    dataset_path = os.path.join('data/preprocessed', filename)
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f'Датасет {dataset_path} не найден')

    dataset = pd.read_csv(
        dataset_path,
        on_bad_lines='skip'
    )

    print(f'{filename}: Downloading audio')

    download_queue = Queue()
    crop_queue = Queue()

    # Init workers
    for _ in range(download_workers):
        Thread(target=download_worker, args=(download_queue, crop_queue, download_dir)).start()
    for _ in range(crop_workers):
        Thread(target=crop_worker, args=(crop_queue, crop_dir)).start()

    # Set download tasks
    for i in range(len(dataset)):
        data = dataset.iloc[i]
        download_queue.put((
            data['YTID'],
            data['start_seconds'],
            data['end_seconds'],
            i
        ))

    # Add stop signal to end of queue
    for _ in range(download_workers):
        download_queue.put(None)
    download_queue.join()
    print('Audio downloading done!')

    for _ in range(crop_workers):
        crop_queue.put(None)
    crop_queue.join()
    print('Audio cropping done!')


def main():
    download_workers = 8
    crop_workers = 8

    audio_dir = 'data/audio'
    if not os.path.isdir(audio_dir):
        os.mkdir(audio_dir)

    download_dir = os.path.join(audio_dir, 'downloaded')
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    crop_dir = os.path.join(audio_dir, 'cropped')
    if not os.path.isdir(crop_dir):
        os.mkdir(crop_dir)

    # 16GB raw, 500MB cropped
    download_audio('eval_segments.csv', download_dir, crop_dir, download_workers, crop_workers)

    # 16GB raw, 500MB cropped
    # download_audio('balanced_train_segments.csv', download_dir, crop_dir, download_workers, crop_workers)

    # 585GB raw, 19GB cropped
    # download_audio('unbalanced_train_segments.csv', download_dir, crop_dir, download_workers, crop_workers)


if __name__ == '__main__':
    main()
