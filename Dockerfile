FROM python:3.7-slim

COPY Pipfile* /home/gbm_api/

WORKDIR /home/gbm_api/

RUN apt-get update && apt-get install -y pipenv

RUN pipenv lock --requirements > requirements.txt

COPY . ./

COPY .env ./

RUN pip3 install -r requirements.txt

RUN pip3 install boto3
RUN pip3 install python_dotenv

EXPOSE 80

CMD ["python3", "-m", "src.app"]
