FROM debian:bookworm-slim

LABEL org.opencontainers.image.title="Vectora Monorepo"
LABEL org.opencontainers.image.description="General monorepo image containing the full Vectora workspace."

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    golang-go \
    nodejs \
    npm \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/vectora

COPY . /workspace/vectora

CMD ["sh"]
