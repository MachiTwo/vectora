FROM jenkins/jenkins:lts-jdk17

USER root

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    docker.io \
    git \
    golang-go \
    nodejs \
    npm \
    python3 \
    python3-pip \
  && pip3 install --no-cache-dir pre-commit \
  && rm -rf /var/lib/apt/lists/*

USER jenkins
