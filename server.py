from fastapi import FastAPI, File, UploadFile, Form
import json
import numpy
import easyocr

# imports for env kafka and redis
from dotenv import load_dotenv
from kafka import  KafkaProducer
import redis
import json
import os

load_dotenv()

REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
KAFKA_HOSTNAME = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT = os.getenv("KAFKA_PORT")

CONTAINER_NAME = 'EASY_OCR'
TOPIC_NAME = "IMAGE_RESULTS"


# Redis initialize
r = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT,
                      password=REDIS_PASSWORD, ssl=True)
# Kafka initialize
producer = KafkaProducer(
    bootstrap_servers=["40.88.35.171:9092"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    api_version=(0, 10, 1)
)

app = FastAPI()

reader = easyocr.Reader(['en'])


@app.post("/easyocr/")
def create_upload_file(file: UploadFile = File(...), image_id: str = Form(...)):

    # Redis Stuff
    r.set(CONTAINER_NAME, "BUSY")

    fileName = file.filename
    contents = file.file.read()
    predictions = recognize(contents)

    response = {
        'image_id': image_id
    }
    text = []
    coords = []
    for idx, prediction in enumerate(predictions):
        cords, word, confidence = prediction
        print(word)
        text.append(word)
        coords.append(cords)
        
    response["data"] = {"text": text, "coords": coords}
    print(response)

     # Redis Kafka Stuff
    r.set(CONTAINER_NAME, "FREE")
    future = producer.send(TOPIC_NAME, value=json.dumps(response, default=convert))
    result = future.get(timeout=60)
    print(result)

    return json.dumps(response, default=convert)


def recognize(img):
    predictions = reader.readtext(img)
    return predictions

def convert(o):
    if isinstance(o, numpy.int64): return int(o)  
    raise TypeError

# uvicorn server:app --host 0.0.0.0 --port 80 --reload