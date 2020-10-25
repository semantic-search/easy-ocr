## RUN IMAGE FROM GHCR 

```sh
docker run -it --env-file .env ghcr.io/semantic-search/easy-ocr:latest
```

Build

```
docker build -t easyocr .
```

Run 

```
docker run --gpus all --env-file .env -it easyocr bash
```

TO clone this repo use this command
```git
    git clone --recurse-submodules https://github.com/semantic-search/easy-ocr.git
```