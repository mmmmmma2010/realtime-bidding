# Use official Python image
FROM python:3.11-slim


# environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# workdir
WORKDIR /app


# install system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc netcat-openbsd && rm -rf /var/lib/apt/lists/*


# copy requirements first (cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt 


# copy project
COPY . /app/


# make entrypoint executable
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


EXPOSE 8000


ENTRYPOINT ["/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "realtime_bidding.asgi:application"]