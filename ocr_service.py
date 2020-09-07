import os
import easyocr


def recognize(img):
    reader = easyocr.Reader(['en'])
    predictions = reader.readtext(img)
    return predictions

def predict(file_name, doc=False):

    predictions = recognize(file_name)

    text = []
    coords = []
    for idx, prediction in enumerate(predictions):
        cords, word, confidence = prediction
        text.append(word)
        coords.append(cords)

    if doc:
        response = {
            "text": text,
            "coords": coords
        }
    else:
        response = {
            "file_name": file_name,
            "text": text,
            "coords": coords,
            "is_doc_type": False
        }
    os.remove(file_name)

    return response