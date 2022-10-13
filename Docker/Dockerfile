FROM python:3.10

RUN useradd -m python

USER python

WORKDIR /home/python

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ./* ./

RUN python -c 'import pipeline'

EXPOSE 5000

CMD python api.py