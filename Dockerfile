FROM python:3.11.5-slim-bookworm

RUN \
    apt update && \
    apt install -y wget curl htop && \
    wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt update && \
    apt install -y dotnet-sdk-6.0 && \
    dotnet tool install ilspycmd -g && \
    rm -rf /var/lib/apt/lists/*

ENV PATH "${PATH}:/root/.dotnet/tools"
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./app ./app

ENTRYPOINT ["python", "/app/app/docker_entrypoint.py"]
