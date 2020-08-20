import json
import numpy
import easyocr

# imports for env kafka and redis
from dotenv import load_dotenv
from kafka import  KafkaProducer
import json
import os

load_dotenv()


KAFKA_HOSTNAME = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT = os.getenv("KAFKA_PORT")

RECEIVE_TOPIC = 'EASY_OCR'
SEND_TOPIC = "IMAGE_RESULTS"

print(f"kafka : {KAFKA_HOSTNAME}:{KAFKA_PORT}")

# To receive img data to process
consumer_easyocr = KafkaConsumer(
    RECEIVE_TOPIC,
    bootstrap_servers=[f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="my-group",
    value_deserializer=lambda x: loads(x.decode("utf-8")),
)

# Send processed img data further 
producer = KafkaProducer(
    bootstrap_servers=[f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

for message in consumer_easyocr:

    reader = easyocr.Reader(['en'])

    message = message.value
    image_id = message['image_id']
    data = message['data']

    data = base64.b64decode(data.encode("ascii"))

    predictions = recognize(data)

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

    
    producer.send(SEND_TOPIC, value=json.dumps(response, default=convert))
    producer.flush()

def recognize(img):
    predictions = reader.readtext(img)
    return predictions

def convert(o):
    if isinstance(o, numpy.int64): return int(o)  
    raise TypeError
