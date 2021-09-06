FROM python:3

RUN mkdir -p /opt/src/applications/user
WORKDIR /opt/src/applications

COPY applications/configuration1.py ./configuration1.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY applications/user/applicationUser.py ./user/application.py

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./user/application.py"]
