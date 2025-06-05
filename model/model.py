from torch import nn


class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer_stack = nn.Sequential(
            nn.Linear(75, 1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.ReLU(),
            nn.Linear(2048, 4096),
            nn.ReLU(),
            nn.Linear(4096, 4096),
            nn.ReLU(),
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, 6),
            nn.Sigmoid()
        )

    def forward(self, x):
        logits = self.layer_stack(x)
        return logits


if __name__ == '__main__':
    import os
    import torch
    from clearml import Task, TaskTypes, OutputModel
    from clearml.model import Framework

    model_name = input("Input model name: ")

    task = Task.init(
        project_name="MuseMood",
        task_name=f"Create model {model_name}",
        task_type=TaskTypes.controller,
        tags=["model creation"],
        auto_resource_monitoring=False,
        auto_connect_frameworks=False
    )
    task.started()

    model = NeuralNetwork()
    print(model)

    # Save and upload to ClearML
    model_weights = "model_weights.pth"
    torch.save(model.state_dict(), model_weights)
    print("Uploading model...")
    out_model = OutputModel(
        task=task,
        framework=Framework.pytorch,
        name=model_name
    )
    out_model.update_weights(
        weights_filename=model_weights,
        upload_uri="https://files.clear.ml",
        auto_delete_file=True,
        async_enable=False
    )
    os.remove(model_weights)

    out_model.publish()

    task.close()
