FROM python:3.9.6-slim

RUN useradd -m -d /home/appuser appuser
USER appuser

WORKDIR /home/appuser

COPY requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

COPY config.json config.json
COPY main.py run.py

CMD [ "python3", "run.py" ]
