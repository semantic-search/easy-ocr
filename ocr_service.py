import os
import easyocr


reader = easyocr.Reader(['en'])
def recognize(img):
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

    os.remove(file_name)

    response = ' '.join(text)
    return response