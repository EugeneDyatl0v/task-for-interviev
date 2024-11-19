FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y gcc
RUN pip install flake8==5.0.4 flake8-import-order==0.18.1  \
    flake8-polyfill==1.0.2 pep8-naming==0.13.3 importlib-metadata==4.11.3

COPY ./ /app/

CMD ["flake8", "."]