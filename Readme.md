Build

```
docker build -t akshay090/ocr:easyocr .
```

Run 

```
docker run --gpus all -v ~/akshay/OCR.Docker:/app -p 80:80 akshay090/ocr:easyocr
```

Test API

```
curl --location --request POST 'http://127.0.0.1:80/uploadfile/' --form 'file=@/home/sign.jpg'
```