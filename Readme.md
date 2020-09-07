Build

```
docker build -t easyocr .
```

Run 

```
docker run --gpus all --env-file .env -it easyocr bash
```

TO clone this remove use this command
```git
    git clone --recurse-submodules https://github.com/semantic-search/easy-ocr.git
```