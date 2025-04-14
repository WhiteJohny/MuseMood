import pandas as pd


def download(download_func, dataset: pd.DataFrame, output_dir: str) -> None:
    counter = 1
    for i in range(len(dataset)):
        data = dataset.iloc[i]
        url = data['YTID']
        start_time = data['start_seconds']
        end_time = data['end_seconds']
        download_func(
            url=url,
            output_dir=output_dir,
            start_time=start_time,
            end_time=end_time,
            counter=counter
        )
        counter += 1
