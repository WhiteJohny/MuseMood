import torch
import clearml
import numpy as np
from device_detector import DEVICE
from model import NeuralNetwork


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


def evaluate_mood(model: NeuralNetwork, features: list[float]) -> np.array:
    """Принимает признаки аудио и выдает оценку настроения музыки"""
    with torch.no_grad():
        inp = torch.tensor(features, dtype=torch.float32, device=DEVICE, requires_grad=False)
        result: torch.Tensor = model(inp)
        return result.cpu().numpy()


if __name__ == '__main__':
    model_name = input("Input model name: ")

    # Ожидаемый результат: [0, 0, 0, 0, 1, 0]
    # Признаки аудио
    features = [
        215.33203125, 0.03170117363333702, 0.0010026624659076333, 0.8944903612136841, 0.09677769988775253,
        -223.00572204589844, 110.0701675415039, 35.715972900390625, 39.40660095214844, 13.58222770690918,
        -5.376039981842041, -10.091299057006836, -1.517043948173523, -14.79349136352539, -4.669361591339111,
        -11.73481559753418, -12.21049690246582, -10.209823608398438, -10.364595413208008, -13.440322875976562,
        -6.061560153961182, -10.26156234741211, -2.0660061836242676, -8.362894058227539, -6.425429344177246,
        92.42302703857422, 30.1351261138916, 18.20677375793457, 14.561868667602539, 9.503901481628418,
        12.590666770935059, 8.072437286376953, 11.516162872314453, 7.059726715087891, 8.830053329467773,
        7.481423377990723, 7.1852641105651855, 7.045202255249023, 6.893896102905273, 8.586373329162598,
        7.235472202301025, 11.99262523651123, 8.159022331237793, 7.977131366729736, 6.904904842376709,
        0.15374968945980072, 0.34928393363952637, 0.0831025093793869, 0.2302461564540863, 0.18078449368476868,
        0.480762779712677, 0.284102201461792, 0.11953020840883255, 0.24936512112617493, 0.18386131525039673,
        0.04399992525577545, 0.03464695066213608, 1314.6015989495593, 723.1404548212278, 2030.9788945267849,
        492.9590287408728, 26.19072197222624, 19.57417490317684, 22.61830992731996, 19.63142177921105,
        19.812140095912646, 20.7943050323297, 49.85286893688813, 5.444618888648296, 3.7265995927889235,
        4.299254745793281, 3.6344273953147574, 3.1361207790842704, 3.6935861777703525, 3.796862804489892
    ]

    model = load_model(model_name)
    results = evaluate_mood(model, features)
    print(results)
