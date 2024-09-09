FROM ghcr.io/penguincloud/core:v5.0.1 AS BUILD
LABEL company="Penguin Tech Group LLC"
LABEL org.opencontainers.image.authors="info@penguintech.group"
LABEL license="GNU AGPL3"

# GET THE FILES WHERE WE NEED THEM!
COPY . /opt/manager/
WORKDIR /opt/manager


# PUT YER ARGS in here
ARG APP_TITLE="PTGAPP" # Change this to actual title for Default

# PUT YER ENVS in here
ENV GATEWAY_CREATION_URL=""
ENV GATEWAY_DELETION_URL=""
ENV GATEWAY_ACTIVATE_URL=""
ENV GATEWAY_SERVER_GET_URL=""
ENV GATEWAY_SERVER_CREATE_URL=""
ENV GATEWAY_SERVER_DELETE_URL=""
ENV TWITCH_HOST=""
ENV TWITCH_PORT=""
ENV TWITCH_PASS=""
ENV TWITCH_NICK=""
ENV TWITCH_AUTH_URL=""
ENV TWITCH_AUTH_CLIENT_ID=""
ENV TWITCH_AUTH_REDIRECT_URI=""
ENV TWITCH_AUTH_RESPONSE_TYPE=""
ENV TWITCH_AUTH_SCOPE=""
ENV DISCORD_TOKEN=""
ENV DISCORD_BOT_INVITE_URL=""

# Python related commands to install dependencies, create a virtual environment, and run the application
RUN apt-get update 
RUN apt-get install -y python3-dev
RUN apt-get install -y libpq-dev
RUN apt-get install -y postgresql


# Set the working directory to the WaddleBot-Configurator directory
WORKDIR /opt/manager/app

# # Install the dependencies in the virtual environment, located in the WaddleBot-Configurator directory
RUN pip install psycopg2-binary
RUN pip install --ignore-installed blinker
RUN pip install -r requirements.txt

# Set the working directory back to the manager directory
WORKDIR /opt/manager/

# BUILD IT!
RUN ansible-playbook build.yml -c local

# Switch to non-root user
USER ptg-user

# Entrypoint time (aka runtime)
ENTRYPOINT ["/bin/bash","/opt/manager/entrypoint.sh"]
