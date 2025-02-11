FROM python:3.11

WORKDIR /home/solis_python

COPY requirements.txt ./                                                                     
RUN pip3 install -r requirements.txt

COPY solis_logging.py ./
COPY secret.json ./

CMD ["python3", "solis_logging.py"]