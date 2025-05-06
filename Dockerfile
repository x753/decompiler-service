FROM python:3.11.5-slim-bookworm

RUN \
    apt update && \
    apt install -y wget curl htop && \
    wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt update && \
    apt install -y dotnet-sdk-8.0 && \
    dotnet tool install ilspycmd -g && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./app/pyproject.toml ./app/poetry.lock ./

RUN pip install -U pip setuptools wheel virtualenv==20.7.2 poetry~=1.4.2 --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 1 && \
    poetry install && \
    rm -rf ~/.cache

COPY ./app ./

ENV PATH "${PATH}:/usr/local/bin/tools"
RUN adduser appuser && cp -r /root/.dotnet/tools /usr/local/bin/tools && chmod 755 /usr/local/bin/tools -R
USER appuser

ENTRYPOINT ["python", "/app/docker_entrypoint.py"]
