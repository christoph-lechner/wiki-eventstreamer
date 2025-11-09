To build the image, run in this directory:
```
docker build -t streamlit .
```

To list the images on your computer, run:
```
docker images
```

To run the image just produced, run (we map the directory `app` in the container as `/app`):
```
docker run -it -p 8501:8501 -v "./app:/app" streamlit
```
