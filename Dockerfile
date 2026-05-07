# Usar imagem oficial do Python 3.12 slim como base
FROM python:3.12-slim

# Evitar a geração de arquivos .pyc e garantir logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema necessárias para PostGIS (GDAL) e drivers de banco de dados
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências Python
# Primeiro copiamos apenas o requirements para aproveitar o cache das camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Configurar o PYTHONPATH para garantir que o módulo 'app' seja encontrado
ENV PYTHONPATH=/app

# Expor a porta padrão do FastAPI
EXPOSE 8000

# O comando padrão será sobrescrito no docker-compose.yml (app vs worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
