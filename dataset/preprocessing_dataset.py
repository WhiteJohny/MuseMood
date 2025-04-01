import pandas as pd

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


def fix_unprocessed_dataset(path: str):
    with open(path, 'r') as f:
        text = f.read().replace(', ', ',')

    with open('edited_' + path, 'w') as f:
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


sentiment_labels = pd.read_csv('class_labels_indices.csv')
sentiment_labels = create_class_labels(sentiment_labels)

fix_unprocessed_dataset('unbalanced_train_segments.csv')
fix_unprocessed_dataset('balanced_train_segments.csv')
fix_unprocessed_dataset('eval_segments.csv')

unprocessed_unbalanced_dataset = pd.read_csv('edited_unbalanced_train_segments.csv', on_bad_lines='skip')
unprocessed_balanced_dataset = pd.read_csv('edited_balanced_train_segments.csv', on_bad_lines='skip')
unprocessed_eval_dataset = pd.read_csv('edited_eval_segments.csv', on_bad_lines='skip')

preprocessing_unbalanced_dataset = create_preprocessing_dataset(unprocessed_unbalanced_dataset, sentiment_labels['mid'])
preprocessing_balanced_dataset = create_preprocessing_dataset(unprocessed_balanced_dataset, sentiment_labels['mid'])
preprocessing_eval_dataset = create_preprocessing_dataset(unprocessed_eval_dataset, sentiment_labels['mid'])

preprocessing_unbalanced_dataset.to_csv(
    'preprocessing_unbalanced_dataset.csv',
    sep=',',
    index=False,
    encoding='utf-8'
)
preprocessing_balanced_dataset.to_csv(
    'preprocessing_balanced_dataset.csv',
    sep=',',
    index=False,
    encoding='utf-8'
)
preprocessing_eval_dataset.to_csv(
    'preprocessing_eval_dataset.csv',
    sep=',',
    index=False,
    encoding='utf-8'
)
