import torch
import clearml

from src.model.device_detector import DEVICE
from src.model.model import NeuralNetwork


def load_model(model_name: str) -> NeuralNetwork:
    """Загружает модель из ClearML"""
    model_query = clearml.Model.query_models(
        model_name=model_name,
        project_name="MuseMood",
        only_published=True,
        max_results=1
    )
    if len(model_query) == 0:
        raise RuntimeError(f'No published models found with name \"{model_name}\"')
    model_weights = model_query[0].get_local_copy(raise_on_error=True, extract_archive=True)

    model = NeuralNetwork().to(DEVICE)
    model.load_state_dict(torch.load(model_weights, weights_only=True))
    model.eval()
    return model


def evaluate_mood(model: NeuralNetwork, features: list[float]) -> str:
    """Принимает признаки аудио и выдает оценку настроения музыки"""
    with torch.no_grad():
        inp = torch.tensor(features, dtype=torch.float32, device=DEVICE, requires_grad=False)
        result: torch.Tensor = model(inp)
        sentiments = " ".join(['1' if i > 0.6 else '0' for i in result.cpu().numpy().tolist()])
        return sentiments
