# Backend - Plataforma FazendaOk

Backend da Plataforma FazendaOk - Sistema de diagnóstico de conformidade socioambiental para propriedades rurais brasileiras.

## 📋 Sobre

Este é o backend da Plataforma FazendaOk, construído com FastAPI e Python 3.11+. O sistema permite verificar a conformidade socioambiental de propriedades rurais brasileiras cruzando dados do CAR (Cadastro Ambiental Rural) com bases de desmatamento (PRODES e DETER do INPE).

## 🏗️ Estrutura do Projeto

```
backend/
├── app/                    # Código da aplicação
│   ├── __init__.py        # Inicialização do pacote
│   ├── main.py            # Aplicação FastAPI principal
│   ├── config.py          # Gerenciamento de configurações
│   ├── api/               # Endpoints da API REST
│   ├── models/            # Modelos do banco de dados (SQLAlchemy)
│   ├── schemas/           # Schemas de validação (Pydantic)
│   ├── services/          # Lógica de negócio
│   ├── tasks/             # Tarefas assíncronas (Celery)
│   └── utils/             # Utilitários
├── alembic/               # Migrações de banco de dados
├── scripts/               # Scripts ETL e utilitários
├── tests/                 # Testes automatizados
├── pyproject.toml         # Configuração do projeto e dependências
├── .env.example           # Exemplo de variáveis de ambiente
└── README.md              # Este arquivo
```

## 🚀 Tecnologias

- **Framework Web**: FastAPI (async Python web framework)
- **ORM**: SQLAlchemy 2.0 com suporte assíncrono
- **Banco de Dados**: PostgreSQL 15 com extensão PostGIS
- **Cache/Fila**: Redis 7+
- **Processamento Assíncrono**: Celery
- **Validação**: Pydantic v2
- **Migrações**: Alembic
- **Armazenamento**: S3-compatible (AWS S3, MinIO, etc.)

## 📦 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 15+ com extensão PostGIS
- Redis 7+
- Acesso a serviço S3-compatible (AWS S3, MinIO, etc.)

### Configuração do Ambiente

1. **Clone o repositório e navegue até o diretório backend:**

```bash
cd backend
```

2. **Crie um ambiente virtual Python:**

```bash
python3 -m venv venv
```

3. **Ative o ambiente virtual:**

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. **Instale as dependências:**

```bash
pip install -e .
```

5. **Configure as variáveis de ambiente:**

Copie o arquivo `.env.example` para `.env` e preencha com os valores reais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure as variáveis obrigatórias:

```bash
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/fazendaok

# Redis
REDIS_URL=redis://localhost:6379/0

# APIs Externas (obtenha as chaves nos respectivos serviços)
INFOSIMPLES_TOKEN=seu_token_aqui
ANTHROPIC_API_KEY=sk-ant-seu_token_aqui
GOOGLE_MAPS_API_KEY=AIza_sua_chave_aqui

# Armazenamento S3
AWS_BUCKET_NAME=fazendaok-photos
AWS_ACCESS_KEY_ID=sua_access_key_aqui
AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui
AWS_ENDPOINT_URL=https://s3.amazonaws.com

# Caminhos dos Shapefiles
PRODES_SHAPEFILE_PATH=/data/prodes_cerrado.shp
DETER_SHAPEFILE_PATH=/data/deter_cerrado.shp
```

## 🏃 Executando a Aplicação

### Desenvolvimento

1. **Inicie o servidor de desenvolvimento:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Acesse a documentação interativa:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Produção

Para produção, use o Gunicorn com workers Uvicorn:

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

## 🗄️ Banco de Dados

### Migrações

O projeto usa Alembic para gerenciar migrações de banco de dados.

**Criar uma nova migração:**

```bash
alembic revision --autogenerate -m "Descrição da migração"
```

**Aplicar migrações:**

```bash
alembic upgrade head
```

**Reverter última migração:**

```bash
alembic downgrade -1
```

### ETL de Dados Geoespaciais

Antes de usar o sistema, é necessário carregar os dados de desmatamento (PRODES e DETER):

**Carregar dados do PRODES:**

```bash
python scripts/load_prodes.py --shapefile /caminho/para/prodes_cerrado.shp --year-filter 2019
```

**Carregar dados do DETER:**

```bash
python scripts/load_deter.py --shapefile /caminho/para/deter_cerrado.shp --months-back 24
```

## 🔄 Processamento Assíncrono (Celery)

O sistema usa Celery para processar tarefas assíncronas como geração de diagnósticos e processamento de fotos.

**Iniciar worker Celery:**

```bash
celery -A app.celery_app worker --loglevel=info
```

**Monitorar tarefas (Flower):**

```bash
celery -A app.celery_app flower
```

Acesse: http://localhost:5555

## 🧪 Testes

### Executar todos os testes:

```bash
pytest
```

### Executar com cobertura:

```bash
pytest --cov=app --cov-report=html
```

### Executar apenas testes unitários:

```bash
pytest -m unit
```

### Executar apenas testes de integração:

```bash
pytest -m integration
```

### Executar testes baseados em propriedades:

```bash
pytest -m property
```

## 📝 Variáveis de Ambiente

### Obrigatórias

- `DATABASE_URL`: URL de conexão com PostgreSQL
- `REDIS_URL`: URL de conexão com Redis

### Opcionais mas Recomendadas

- `INFOSIMPLES_TOKEN`: Token para API da Infosimples (acesso ao SICAR)
- `ANTHROPIC_API_KEY`: Chave da API Anthropic (Claude AI)
- `GOOGLE_MAPS_API_KEY`: Chave da API Google Maps
- `AWS_BUCKET_NAME`: Nome do bucket S3
- `AWS_ACCESS_KEY_ID`: Access Key ID do AWS
- `AWS_SECRET_ACCESS_KEY`: Secret Access Key do AWS
- `AWS_ENDPOINT_URL`: URL do endpoint S3 (opcional)
- `PRODES_SHAPEFILE_PATH`: Caminho para shapefile do PRODES
- `DETER_SHAPEFILE_PATH`: Caminho para shapefile do DETER

### Configurações da Aplicação

- `MAX_FOTO_SIZE_MB`: Tamanho máximo de foto em MB (padrão: 10)
- `MAX_FOTOS_POR_UPLOAD`: Número máximo de fotos por upload (padrão: 20)
- `LOG_LEVEL`: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `RATE_LIMIT_PER_HOUR`: Limite de requisições por hora (padrão: 100)
- `DIAGNOSTIC_CACHE_TTL_SECONDS`: TTL do cache de diagnósticos (padrão: 21600 = 6 horas)

## 🔧 Desenvolvimento

### Formatação de Código

O projeto usa Black para formatação:

```bash
black app/
```

### Linting

O projeto usa Ruff para linting:

```bash
ruff check app/
```

### Type Checking

O projeto usa MyPy para verificação de tipos:

```bash
mypy app/
```

## 📚 Documentação da API

A documentação completa da API está disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

#### Propriedades

- `POST /api/v1/properties/search/car` - Buscar propriedade por número CAR
- `POST /api/v1/properties/search/coordinates` - Buscar propriedade por coordenadas
- `POST /api/v1/properties/search/address` - Buscar propriedade por endereço

#### Diagnósticos

- `POST /api/v1/diagnostics/generate/{property_id}` - Gerar diagnóstico
- `GET /api/v1/diagnostics/status/{task_id}` - Verificar status do diagnóstico
- `GET /api/v1/diagnostics/{diagnostic_id}` - Obter diagnóstico completo
- `GET /api/v1/diagnostics/history/{car_number}` - Histórico de diagnósticos

#### Fotos

- `POST /api/v1/photos/upload/{property_id}` - Upload de fotos
- `GET /api/v1/photos/{property_id}` - Listar fotos da propriedade

#### Relatórios

- `GET /api/v1/reports/{diagnostic_id}/pdf` - Baixar relatório em PDF

#### Sistema

- `GET /` - Informações sobre a API
- `GET /saude` - Health check
- `GET /info` - Informações de configuração

## 🐳 Docker

### Construir imagem:

```bash
docker build -t fazendaok-backend .
```

### Executar container:

```bash
docker run -p 8000:8000 --env-file .env fazendaok-backend
```

### Docker Compose:

Veja o arquivo `docker-compose.yml` na raiz do projeto para executar todos os serviços.

## 🤝 Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
2. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
3. Push para a branch (`git push origin feature/nova-funcionalidade`)
4. Abra um Pull Request

## 📄 Licença

MIT

## 👥 Equipe

FazendaOk Team

## 📞 Suporte

Para suporte, envie um email para contato@fazendaok.com.br

---

**Task 1 Completa**: Backend project structure and core configuration ✅

- ✅ Estrutura de diretórios criada
- ✅ `pyproject.toml` configurado com todas as dependências
- ✅ `app/__init__.py`, `app/main.py`, `app/config.py` implementados
- ✅ Carregamento de configurações via variáveis de ambiente
- ✅ `.env.example` criado com todas as variáveis necessárias
- ✅ Validação de variáveis obrigatórias na inicialização
- ✅ Documentação completa no README
