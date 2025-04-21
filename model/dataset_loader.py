from torch.utils.data import Dataset
import pandas as pd
import numpy as np


class MuseMoodDataset(Dataset):
    def __init__(self, filepath, transform=None, target_transform=None):
        self.data = pd.read_csv(filepath)
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Convert list string representation ("[1, 2, 3]") to numpy array
        X = np.fromstring(self.data.iloc[idx, 0][1:-1], dtype=np.float32, sep=', ')

        Y = np.array(self.data.iloc[idx, 1:], dtype=np.float32)
        if self.transform:
            X = self.transform(X)
        if self.target_transform:
            Y = self.target_transform(Y)
        return X, Y


if __name__ == '__main__':

    from torch.utils.data import DataLoader

    # Load dataset
    training_data = MuseMoodDataset("../dataset/data/processed/unbalanced_train_segments.csv")
    test_data = MuseMoodDataset("../dataset/data/processed/eval_segments.csv")

    # Init DataLoaders to iterate through dataset
    train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=64, shuffle=True)

    # Print data shape to test if dataset loaded correctly
    train_features, train_labels = next(iter(train_dataloader))
    print(f"Feature batch shape: {train_features.size()}")
    print(f"Labels batch shape: {train_labels.size()}")
