
#!/bin/sh

sudo docker run -it -p 8501:8501 -v ./app:/app streamlit
