import pandas as pd
import os
import shutil

from audio_parsers.download_audio import download
from audio_parsers.yt_link import download_audio_as_wav
from audio_converter.make_dataset import make_dataset


LINK_PATTERN = 'https://www.youtube.com/watch?v='
SENTIMENTS = ['funny', 'happy', 'sad', 'scary', 'tender', 'trance']


def check_for_sentiment(row: str) -> bool:
    for sentiment in SENTIMENTS:
        if sentiment in row.lower():
            return True
    return False


def create_class_labels(data: pd.DataFrame) -> pd.DataFrame:
    labels = []
    for i in range(len(data)):
        label = data.iloc[i]['display_name']
        if check_for_sentiment(label):
            labels.append([data.iloc[i]['index'], label, data.iloc[i]['mid']])
    return pd.DataFrame(labels, columns=['index', 'display_name', 'mid'])


def fix_unprocessed_dataset(path: str, name_dir: str) -> None:
    with open(path, 'r') as f:
        text = f.read().replace(', ', ',')

    if not os.path.isdir(name_dir):
        os.mkdir(name_dir)

    with open(name_dir + '/edited_' + path[path.index('/') + 1:], 'w') as f:
        f.write(text)


def create_preprocessing_dataset(data: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    new_data = []
    for i in range(len(data)):
        labels_counter = {
            '/t/dd00032': 0,
            '/t/dd00031': 0,
            '/t/dd00033': 0,
            '/t/dd00037': 0,
            '/t/dd00034': 0,
            '/m/07lnk': 0
        }

        curr_data = data.iloc[i]
        for label in labels:
            if label in curr_data['positive_labels']:
                labels_counter[label] = 1

        if 1 in labels_counter.values():
            new_data.append(
                [
                    LINK_PATTERN + curr_data['YTID'],
                    curr_data['start_seconds'],
                    curr_data['end_seconds']
                ]
            )
            new_data[-1].extend(labels_counter.values())

    return pd.DataFrame(
        new_data,
        columns=[
            'YTID',
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


file_path = 'raw_data/class_labels_indices.csv'
sentiment_labels = pd.read_csv(file_path)
sentiment_labels = create_class_labels(sentiment_labels)

dir_name = 'edited_data'
fix_unprocessed_dataset('raw_data/unbalanced_train_segments.csv', dir_name)
fix_unprocessed_dataset('raw_data/balanced_train_segments.csv', dir_name)
fix_unprocessed_dataset('raw_data/eval_segments.csv', dir_name)

file_path = 'edited_data/edited_unbalanced_train_segments.csv'
unprocessed_unbalanced_dataset = pd.read_csv(
    file_path,
    on_bad_lines='skip'
)

file_path = 'edited_data/edited_balanced_train_segments.csv'
unprocessed_balanced_dataset = pd.read_csv(
    file_path,
    on_bad_lines='skip'
)

file_path = 'edited_data/edited_eval_segments.csv'
unprocessed_eval_dataset = pd.read_csv(
    file_path,
    on_bad_lines='skip'
)

preprocessing_unbalanced_dataset = create_preprocessing_dataset(unprocessed_unbalanced_dataset, sentiment_labels['mid'])
preprocessing_balanced_dataset = create_preprocessing_dataset(unprocessed_balanced_dataset, sentiment_labels['mid'])
preprocessing_eval_dataset = create_preprocessing_dataset(unprocessed_eval_dataset, sentiment_labels['mid'])

dir_name = 'preprocessing_data'
if not os.path.isdir(dir_name):
    os.mkdir(dir_name)

file_path = dir_name + '/preprocessing_unbalanced_dataset.csv'
preprocessing_unbalanced_dataset.to_csv(
    file_path,
    sep=',',
    index=False,
    encoding='utf-8'
)

file_path = dir_name + '/preprocessing_balanced_dataset.csv'
preprocessing_balanced_dataset.to_csv(
    file_path,
    sep=',',
    index=False,
    encoding='utf-8'
)

file_path = dir_name + '/preprocessing_eval_dataset.csv'
preprocessing_eval_dataset.to_csv(
    file_path,
    sep=',',
    index=False,
    encoding='utf-8'
)

preprocessed_unbalanced_dataset = pd.read_csv('preprocessing_data/preprocessing_unbalanced_dataset.csv')
preprocessed_balanced_dataset = pd.read_csv('preprocessing_data/preprocessing_balanced_dataset.csv')
preprocessed_eval_dataset = pd.read_csv('preprocessing_data/preprocessing_eval_dataset.csv')


# dir_name = 'unbalanced_audio'
# if os.path.isdir(dir_name):
#     shutil.rmtree(dir_name)
# download(download_audio_as_wav, preprocessed_unbalanced_dataset, dir_name)
# make_dataset(dir_name, 'unbalanced_dataset.csv', preprocessed_unbalanced_dataset)
#
# dir_name = 'balanced_audio'
# if os.path.isdir(dir_name):
#     shutil.rmtree(dir_name)
# download(download_audio_as_wav, preprocessed_balanced_dataset, dir_name)
# make_dataset(dir_name, 'balanced_dataset.csv', preprocessed_balanced_dataset)
#
# dir_name = 'eval_audio'
# if os.path.isdir(dir_name):
#     shutil.rmtree(dir_name)
# download(download_audio_as_wav, preprocessed_eval_dataset, 'eval_audio')
# make_dataset(dir_name, 'eval_dataset.csv', preprocessed_eval_dataset)
#
# # Вектор из строки в np.ndarray (пример)
# # df = pd.read_csv("data.csv")
# # features_vector = np.array(eval(df["features"][0]))
#
# shutil.rmtree('edited_data')
# shutil.rmtree('preprocessing_data')
# shutil.rmtree('unbalanced_audio')
# shutil.rmtree('balanced_audio')
# shutil.rmtree('eval_audio')
