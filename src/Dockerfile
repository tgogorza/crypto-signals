FROM python:2.7-slim-jessie

ENV PYTHONUNBUFFERED=0
ADD ./* /
RUN pip install -r requirements.txt

CMD python auto_trade.py