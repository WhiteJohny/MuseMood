import pandas as pd
import os

SENTIMENTS = ['funny', 'happy', 'sad', 'scary', 'tender', 'trance']

DIR_RAW = 'data/raw'
DIR_EDITED = 'data/edited'
DIR_PREPROCESSED = 'data/preprocessed'


def check_for_sentiment(row: str) -> bool:
    for sentiment in SENTIMENTS:
        if sentiment in row.lower():
            return True
    return False


def load_class_labels() -> pd.DataFrame:
    data = pd.read_csv(os.path.join(DIR_RAW, 'class_labels_indices.csv'))

    labels = []
    for i in range(len(data)):
        label = data.iloc[i]['display_name']
        if check_for_sentiment(label):
            labels.append([data.iloc[i]['index'], label, data.iloc[i]['mid']])
    return pd.DataFrame(labels, columns=['index', 'display_name', 'mid'])


def fix_unprocessed_dataset(filename: str) -> None:
    with open(os.path.join(DIR_RAW, filename), 'r') as f:
        text = f.read().replace(', ', ',')

    with open(os.path.join(DIR_EDITED, filename), 'w') as f:
        f.write(text)


def create_preprocessed_dataset(data: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
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
                    curr_data['YTID'],
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


def preprocess_dataset(filename: str, labels: pd.DataFrame):
    print(f'Preprocessing dataset: {filename}')

    fix_unprocessed_dataset(filename)

    unprocessed_dataset = pd.read_csv(
        os.path.join(DIR_EDITED, filename),
        on_bad_lines='skip'
    )

    preprocessed_dataset = create_preprocessed_dataset(unprocessed_dataset, labels['mid'])

    preprocessed_dataset.to_csv(
        os.path.join(DIR_PREPROCESSED, filename),
        sep=',',
        index=False,
        encoding='utf-8'
    )

    print('Preprocessing done!')


def main():
    if not os.path.exists(DIR_EDITED): os.mkdir(DIR_EDITED)
    if not os.path.exists(DIR_PREPROCESSED): os.mkdir(DIR_PREPROCESSED)

    sentiment_labels = load_class_labels()
    preprocess_dataset('eval_segments.csv', sentiment_labels)
    preprocess_dataset('balanced_train_segments.csv', sentiment_labels)
    # preprocess_dataset('unbalanced_train_segments.csv', sentiment_labels)


if __name__ == '__main__':
    main()
