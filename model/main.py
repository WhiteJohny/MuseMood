import os
import torch
from torch.utils.data import DataLoader
from clearml import Task, Dataset, OutputModel
from clearml.model import Framework
from device_detector import DEVICE
from dataset_loader import MuseMoodDataset
from model import NeuralNetwork
from train import train


def run_train_task(task: Task):
    task.started()
    print(f"Running task {task.name} (ID: {task.task_id})")

    # Get task details, download files
    input_models = task.get_models()['input']
    if len(input_models) == 0:
        raise RuntimeError("No input model assigned to training task")
    model_weights = input_models[0].get_weights(raise_on_error=True, extract_archive=True)

    train_folder = Dataset.get(
        dataset_name="MuseMood_unbalanced",
        dataset_project="MuseMood"
    ).get_local_copy(raise_on_error=True)

    eval_folder = Dataset.get(
        dataset_name="MuseMood_eval",
        dataset_project="MuseMood"
    ).get_local_copy(raise_on_error=True)

    params = task.get_parameters()

    # Load everything in
    model = NeuralNetwork().to(DEVICE)
    model.load_state_dict(torch.load(model_weights, weights_only=True))

    training_data = MuseMoodDataset(os.path.join(train_folder, "unbalanced_train_segments.csv"))
    test_data = MuseMoodDataset(os.path.join(eval_folder, "eval_segments.csv"))

    batch_size = int(params['General/batch_size'])
    learning_rate = float(params['General/learning_rate'])
    epochs = int(params['General/iterations'])
    out_model_name = params['General/output_model_name']

    # Train model
    train(
        train_dataloader=DataLoader(training_data, batch_size=batch_size),
        test_dataloader=DataLoader(test_data, batch_size=batch_size),
        model=model,
        loss_fn=torch.nn.MSELoss(),
        optimizer=torch.optim.SGD(model.parameters(), lr=learning_rate),
        epochs=epochs,
        logger=task.logger
    )

    # Save and upload to ClearML
    model_weights = "model_weights.pth"
    torch.save(model.state_dict(), model_weights)
    print("Uploading model...")
    out_model = OutputModel(
        task=task,
        framework=Framework.pytorch,
        name=out_model_name
    )
    out_model.update_weights(
        weights_filename=model_weights,
        upload_uri="https://files.clear.ml",
        auto_delete_file=True,
        async_enable=False
    )
    os.remove(model_weights)

    task.close()


if __name__ == '__main__':
    task_name = input("Input task name: ")
    task = Task.get_task(task_name=task_name, project_name="MuseMood")
    if task is None:
        print("Task not found, creating a new one...")
        task = Task.init(
            project_name="MuseMood",
            task_name=task_name,
            auto_connect_frameworks=False
        )
        model_name = input("Input model name: ")
        task.set_input_model(model_name=model_name)
        task.set_parameters(
            batch_size=int(input("Batch size: ")),
            learning_rate=float(input("Learning rate: ")),
            iterations=int(input("Iterations: ")),
            output_model_name=input("Output model name: ")
        )
    else:
        print("Existing task found")

    print(f"Task ID: {task.task_id}")
    input("Verify task parameters and press enter to continue...")
    run_train_task(task)
