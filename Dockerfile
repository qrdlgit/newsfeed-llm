# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy your Python application code into the container
COPY *.py /app
COPY requirements.txt /app
COPY settings.json /app
COPY models /app/models
COPY *.sh /app
COPY logrotate.conf /etc/logrotate.d

COPY my-crontab /etc/cron.d/my-crontab
COPY my-script.sh /usr/local/bin/my-script.sh
RUN chmod 0644 /etc/cron.d/my-crontab
RUN chmod +x /usr/local/bin/my-script.sh

RUN apk add --no-cache logrotate
RUN apk add --no-cache dcron


# Install required packages using pip
RUN pip install --no-cache-dir numpy scipy sentence_transformers scikit-learn

RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your Python program
ENTRYPOINT ["./run.sh"]

