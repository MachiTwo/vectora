---
title: "VPS Deployment"
slug: vps-deployment
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - deployment
  - linux
  - production
  - ssl
  - systemd
  - vps
  - vectora
---

{{< lang-toggle >}}

Deploy Vectora em um VPS Linux (DigitalOcean, Linode, AWS EC2, Hetzner, etc) rodando PostgreSQL + Redis + Vectora como serviço systemd.

## Checklist Pré-Deployment

- [ ] VPS com **Ubuntu 22.04 LTS** ou similar
- [ ] SSH acesso como user sem root privileges
- [ ] **4GB RAM mínimo** (8GB+ recomendado)
- [ ] **20GB+ SSD** (para LanceDB + dados)
- [ ] Domínio DNS apontando para VPS IP

## Setup do VPS

### 1. Atualizar Sistema

```bash
ssh ubuntu@your-vps-ip

sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential python3.12 python3.12-venv python3-pip \
    postgresql postgresql-contrib redis-server nginx curl wget git
```

### 2. Configurar PostgreSQL

```bash
# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql << EOF
CREATE USER vectora WITH PASSWORD 'secure-password-here';
CREATE DATABASE vectora OWNER vectora;
ALTER DATABASE vectora SET client_encoding TO 'utf8';
ALTER DATABASE vectora SET default_transaction_isolation TO 'read committed';
\q
EOF

# Verificar
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname = 'vectora';"
```

### 3. Configurar Redis

```bash
# Iniciar serviço
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar
redis-cli ping
# PONG
```

### 4. Criar User Vectora (Não-root)

```bash
sudo useradd -m -s /bin/bash vectora
sudo usermod -aG sudo vectora
su - vectora
```

### 5. Instalar Vectora

```bash
# Como user vectora
python3.12 -m venv ~/vectora-env
source ~/vectora-env/bin/activate

pip install --upgrade pip
pip install vectora

# Verificar
vectora --version
```

### 6. Configurar Variáveis de Ambiente

```bash
# ~/vectora-env.sh
export ANTHROPIC_API_KEY="sk-ant-xxx"
export VOYAGE_API_KEY="sk-voyage-xxx"
export DATABASE_URL="postgresql://vectora:secure-password-here@localhost:5432/vectora"
export REDIS_HOST="127.0.0.1"
export REDIS_PORT=6379
export LANCEDB_PATH="/home/vectora/vectora-data"
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-sonnet-4-6"
```

Adicionar ao `.bashrc`:

```bash
echo "source ~/vectora-env.sh" >> ~/.bashrc
source ~/.bashrc
```

### 7. Inicializar Banco

```bash
vectora init
vectora health
# Verificar que tudo está ok
```

## Systemd Service

Crie `/etc/systemd/system/vectora.service`:

```ini
[Unit]
Description=Vectora RAG Server
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=notify
User=vectora
WorkingDirectory=/home/vectora
Environment="PATH=/home/vectora/vectora-env/bin"
EnvironmentFile=/home/vectora/vectora-env.sh
ExecStart=/home/vectora/vectora-env/bin/vectora serve --host 0.0.0.0 --port 8000

# Restart policy
Restart=on-failure
RestartSec=10s
StartLimitIntervalSec=60s
StartLimitBurst=5

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/home/vectora/vectora-data

[Install]
WantedBy=multi-user.target
```

Ativar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vectora
sudo systemctl start vectora

# Verificar status
sudo systemctl status vectora
journalctl -u vectora -f  # Ver logs
```

## Nginx Reverse Proxy

Crie `/etc/nginx/sites-available/vectora`:

```nginx
upstream vectora_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (Let's Encrypt via Certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    location / {
        proxy_pass http://vectora_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Streaming
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://vectora_backend/health;
        access_log off;
    }
}
```

Ativar site:

```bash
sudo ln -s /etc/nginx/sites-available/vectora /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL com Let's Encrypt

Instalar Certbot e obter certificado:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Firewall

Configurar UFW:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verificar
sudo ufw status
```

## Backups Automáticos

Script de backup diário (`~/backup.sh`):

```bash
#!/bin/bash

BACKUP_DIR="/home/vectora/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump postgresql://vectora:password@localhost/vectora | \
    gzip > $BACKUP_DIR/vectora-db-$(date +%Y%m%d).sql.gz

# Backup LanceDB
tar czf $BACKUP_DIR/vectora-data-$(date +%Y%m%d).tar.gz \
    ~/vectora-data

# Manter últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed at $(date)"
```

Agendar via crontab:

```bash
# Como user vectora
crontab -e

# Adicionar linha:
0 2 * * * /home/vectora/backup.sh >> /home/vectora/backup.log 2>&1
```

## Monitoramento

Ver uso de recursos:

```bash
# CPU, memória
top -b -n 1 | head -20

# Disco
df -h

# PostgreSQL conexões
psql -U vectora -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memória
redis-cli INFO memory
```

## Troubleshooting

### Vectora não inicia

```bash
sudo systemctl status vectora
journalctl -u vectora -n 50
# Verificar errors específicos
```

### Conexão PostgreSQL falha

```bash
psql -U vectora -d vectora -c "SELECT 1"
# Se falhar, verificar credenciais em .env.sh
```

### Nginx mostra erro 502

```bash
curl http://127.0.0.1:8000/health
# Se falhar, Vectora não está respondendo
sudo systemctl restart vectora
```

### Alta latência

```bash
# Monitorar load
load=$(cat /proc/loadavg | awk '{print $1}')
# Se > num_cpus, sistema está overloaded
```

## Production Checklist

- [ ] SSL certificate configurado
- [ ] Backups automáticos rodando diariamente
- [ ] Firewall habilitado
- [ ] PostgreSQL com pool_size otimizado
- [ ] Redis maxmemory configurado
- [ ] Logs configurados em `/var/log/vectora`
- [ ] Alertas/monitoring configurado (Uptime Robot, Grafana)
- [ ] Rate limiting habilitado no Nginx

## External Linking

| Conceito              | Recurso                      | Link                                                                                        |
| --------------------- | ---------------------------- | ------------------------------------------------------------------------------------------- |
| **Ubuntu Server**     | Linux distribution           | [ubuntu.com/server](https://ubuntu.com/server)                                              |
| **systemd**           | Linux service management     | [freedesktop.org/wiki/Software/systemd](https://www.freedesktop.org/wiki/Software/systemd/) |
| **Nginx**             | Web server and reverse proxy | [nginx.org/docs](https://nginx.org/en/docs/)                                                |
| **Let's Encrypt**     | Free SSL certificates        | [letsencrypt.org](https://letsencrypt.org/)                                                 |
| **PostgreSQL Backup** | Database backup strategies   | [postgresql.org/docs/current/backup](https://www.postgresql.org/docs/current/backup.html)   |
