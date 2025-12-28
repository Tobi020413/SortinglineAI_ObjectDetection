import cv2
import numpy as np
import time

print("lib.ki_integration wurde importiert")


from tflite_runtime.interpreter import Interpreter


# Pfade auf dem TXT
MODEL_PATH = "/opt/ft/workspaces/machine-learning-b/model.tflite"
LABELS_PATH = "/opt/ft/workspaces/machine-learning-b/labels.txt"
SCORE_THRESHOLD = 0.5

_interpreter = None
_input_details = None
_output_details = None
_input_h = None
_input_w = None
_labels = None


def load_labels(path):
    labels = []
    f = open(path, "r")
    for line in f:
        line = line.strip()
        if line != "":
            labels.append(line)
    f.close()
    return labels

def init_model():
    global _interpreter, _input_details, _output_details, _input_h, _input_w, _labels

    print("init_model() aufgerufen")

    _labels = load_labels(LABELS_PATH)

    _interpreter = Interpreter(model_path=MODEL_PATH)
    _interpreter.allocate_tensors()

    _input_details = _interpreter.get_input_details()
    _output_details = _interpreter.get_output_details()

    shape = _input_details[0]["shape"]   # [1, H, W, 3]
    _input_h = shape[1]
    _input_w = shape[2]

    print("Modell geladen. Erwartete Eingabegröße: {}x{}".format(_input_w, _input_h))


def run_inference(frame):
    """
    Nimmt ein Kamerabild (NumPy-Array vom TXT) und gibt eine Liste von
    Detections zurück:
    [
      {"label": str, "score": float, "position": [x1, y1, x2, y2]},
      ...
    ]
    Die Position ist in Pixeln relativ zu der Größe, die ins Modell geht (_input_w x _input_h).
    """

    global _interpreter, _input_details, _output_details, _input_h, _input_w, _labels

    if _interpreter is None:
        raise RuntimeError("Modell ist nicht initialisiert. Bitte init_model() aufrufen.")

    # Bild auf Eingangsgröße des Modells skalieren
    img_resized = cv2.resize(frame, (_input_w, _input_h))

    # Datentyp anpassen
    if _input_details[0]["dtype"] == np.float32:
        img_input = img_resized.astype(np.float32) / 255.0
    else:
        img_input = img_resized.astype(np.uint8)

    img_input = np.expand_dims(img_input, axis=0)

    # Inference
    _interpreter.set_tensor(_input_details[0]["index"], img_input)
    _interpreter.invoke()

    # Outputs holen
    scores_raw  = _interpreter.get_tensor(_output_details[0]["index"])  # (1,25)
    boxes_raw   = _interpreter.get_tensor(_output_details[1]["index"])  # (1,25,4)
    num_raw     = _interpreter.get_tensor(_output_details[2]["index"])  # (1,)
    classes_raw = _interpreter.get_tensor(_output_details[3]["index"])  # (1,25)

    num_det = int(num_raw[0])
    scores  = scores_raw[0][:num_det]
    boxes   = boxes_raw[0][:num_det]
    classes = classes_raw[0][:num_det]

    detections = []

    for i in range(num_det):
        score = float(scores[i])
        if score < SCORE_THRESHOLD:
            continue

        cls_id = int(classes[i])
        if cls_id >= 0 and cls_id < len(_labels):
            label_name = _labels[cls_id]
        else:
            label_name = "id_{}".format(cls_id)

        ymin, xmin, ymax, xmax = boxes[i]  # normalisiert 0..1

        # In Pixelkoordinaten bezogen auf _input_w/_input_h
        x1 = int(xmin * _input_w)
        y1 = int(ymin * _input_h)
        x2 = int(xmax * _input_w)
        y2 = int(ymax * _input_h)

        detections.append({
            "label": label_name,
            "score": score,
            "position": [x1, y1, x2, y2],
        })

    # Nach Score sortieren, bester zuerst
    detections.sort(key=lambda d: d["score"], reverse=True)

    return detections, img_resized
