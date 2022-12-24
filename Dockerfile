FROM python:3

RUN pip install python-telegram-bot -U --pre
RUN pip install matplotlib

COPY . .

ENTRYPOINT ["python3", "./main.py", '5674494549:AAGBjydRKDmSjrwre9uzTvdPbh-ZeCOrIM4']
