import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from clearml import Logger
from device_detector import DEVICE


def train_epoch(dataloader, model, loss_fn, optimizer, logger, iteration):
    num_batches = len(dataloader)

    # Set model to training mode
    model.train()

    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(DEVICE), y.to(DEVICE)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        # Print progress every few batches
        if batch % 25 == 0:
            print(f"loss: {loss:>7f}  [batch {batch:>5d}/{num_batches:>5d}]")
        if logger is not None:
            logger.report_scalar("Loss", "Train", loss, iteration)


def test(dataloader, model, loss_fn, logger, iteration):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)

    # Set model to evaluation mode
    model.eval()

    test_loss, correct = 0, 0

    #  Disable gradient calculation for better performance
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(DEVICE), y.to(DEVICE)
            pred: torch.Tensor = model(X)
            test_loss += loss_fn(pred, y).item()
            if (pred - y).abs().max().item() < 0.5:
                correct += 1
    test_loss /= num_batches
    accuracy = 100 * correct / size

    print(f"Test Error: \n Accuracy: {accuracy:>0.1f}%, Avg loss: {test_loss:>8f} \n")
    if logger is not None:
        logger.report_scalar("Loss", "Test", test_loss, iteration)
        logger.report_scalar("Accuracy", "Test", accuracy, iteration)


def train(
        train_dataloader: DataLoader,
        test_dataloader: DataLoader,
        model: nn.Module,
        loss_fn: nn.modules.loss._Loss,
        optimizer: torch.optim.Optimizer,
        epochs: int,
        logger: Logger = None
):
    for t in range(epochs):
        print(f"Epoch {t + 1}\n-------------------------------")
        train_epoch(train_dataloader, model, loss_fn, optimizer, logger, t)
        test(test_dataloader, model, loss_fn, logger, t)
    print("Done!")


if __name__ == '__main__':
    from model import NeuralNetwork
    from dataset_loader import MuseMoodDataset

    batch_size = 64
    learning_rate = 1e-3
    epochs = 10

    # Load dataset
    training_data = MuseMoodDataset("../dataset/data/processed/unbalanced_train_segments.csv")
    test_data = MuseMoodDataset("../dataset/data/processed/eval_segments.csv")

    # Load model
    model_path = "model_parameters.pth"
    model = NeuralNetwork().to(DEVICE)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, weights_only=True))

    train(
        train_dataloader=DataLoader(training_data, batch_size=batch_size),
        test_dataloader=DataLoader(test_data, batch_size=batch_size),
        model=model,
        loss_fn=nn.MSELoss(),
        optimizer=torch.optim.SGD(model.parameters(), lr=learning_rate),
        epochs=epochs
    )

    torch.save(model.state_dict(), model_path)
