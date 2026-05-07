# FazendaOk Platform - Backend

## Visão Geral

Backend da Plataforma FazendaOk construído com FastAPI, PostgreSQL + PostGIS, Redis e Celery.

A plataforma permite verificar a conformidade socioambiental de propriedades rurais brasileiras cruzando dados do CAR (Cadastro Ambiental Rural) com bases de desmatamento (PRODES e DETER do INPE).

## Estrutura do Projeto

```
app/
├── __init__.py              # Inicialização do pacote
├── main.py                  # Aplicação FastAPI principal
├── config.py                # Configurações (variáveis de ambiente)
├── database.py              # Configuração do banco de dados
├── celery_app.py            # Configuração do Celery
├── api/                     # Endpoints da API REST
│   └── v1/                  # API versão 1
│       ├── properties.py    # Endpoints de propriedades
│       ├── diagnostics.py   # Endpoints de diagnósticos
│       ├── photos.py        # Endpoints de fotos
│       └── dashboard.py     # Endpoint de dashboard
├── models/                  # Modelos SQLAlchemy (banco de dados)
│   ├── property.py          # Modelo de Propriedade
│   ├── diagnostic.py        # Modelo de Diagnóstico
│   ├── photo.py             # Modelo de Foto
│   ├── prodes.py            # Modelo de dados PRODES
│   └── deter.py             # Modelo de dados DETER
├── schemas/                 # Schemas Pydantic (validação)
│   ├── property.py          # Schemas de propriedade
│   ├── diagnostic.py        # Schemas de diagnóstico
│   ├── photo.py             # Schemas de foto
│   └── dashboard.py         # Schemas de dashboard
├── services/                # Lógica de negócio
│   ├── sicar_service.py     # Integração com SICAR (Infosimples)
│   ├── spatial_service.py   # Análise espacial (PostGIS)
│   ├── photo_service.py     # Processamento de fotos
│   └── claude_service.py    # Integração com Claude AI (futuro)
└── tasks/                   # Tarefas assíncronas (Celery)
    └── photo_tasks.py       # Tarefas de processamento de fotos
```

## Tecnologias Utilizadas

- **FastAPI**: Framework web assíncrono moderno
- **PostgreSQL + PostGIS**: Banco de dados com suporte geoespacial
- **SQLAlchemy**: ORM com suporte assíncrono
- **Alembic**: Gerenciamento de migrações de banco de dados
- **Celery**: Processamento assíncrono de tarefas
- **Redis**: Cache e message broker
- **Pydantic**: Validação de dados
- **Boto3**: Upload de fotos para S3
- **Pillow**: Processamento de imagens e extração de EXIF
- **Anthropic SDK**: Integração com Claude AI
- **HTTPX**: Cliente HTTP assíncrono

## Configuração

### 1. Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha com os valores reais:

```bash
cp .env.example .env
```

Variáveis obrigatórias:
- `DATABASE_URL`: URL de conexão com PostgreSQL
- `REDIS_URL`: URL de conexão com Redis
- `INFOSIMPLES_TOKEN`: Token da API Infosimples (acesso ao SICAR)
- `ANTHROPIC_API_KEY`: Chave da API Anthropic (Claude AI)
- `GOOGLE_MAPS_API_KEY`: Chave da API Google Maps
- `AWS_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: Credenciais S3

### 2. Instalação de Dependências

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Banco de Dados

```bash
# Executar migrações (quando disponíveis)
alembic upgrade head
```

### 4. Executar a Aplicação

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar servidor de desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

### 5. Executar Worker Celery

Em outro terminal:

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar worker Celery
celery -A app.celery_app worker --loglevel=info
```

## Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principais

### Propriedades
- `POST /api/v1/properties/search/car` - Buscar propriedade por número CAR
- `POST /api/v1/properties/search/coordinates` - Buscar propriedade por coordenadas
- `GET /api/v1/properties/{property_id}` - Obter detalhes de uma propriedade

### Diagnósticos
- `POST /api/v1/diagnostics/generate/{property_id}` - Gerar diagnóstico
- `GET /api/v1/diagnostics/{diagnostic_id}` - Obter diagnóstico
- `GET /api/v1/diagnostics/history/{car_number}` - Histórico de diagnósticos

### Fotos
- `POST /api/v1/photos/upload/{property_id}` - Upload de fotos
- `GET /api/v1/photos/{property_id}` - Listar fotos de uma propriedade

### Dashboard
- `GET /api/v1/dashboard/overview` - Visão geral do sistema

## Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app --cov-report=html

# Executar testes específicos
pytest app/services/test_photo_service.py
```

## Requisitos Atendidos

Esta implementação atende aos seguintes requisitos da especificação:

- **16.1**: Carregamento de configuração via variáveis de ambiente
- **16.2**: Configuração do DATABASE_URL
- **16.3**: Configuração do REDIS_URL
- **16.4**: Configuração do INFOSIMPLES_TOKEN
- **16.5**: Configuração do ANTHROPIC_API_KEY
- **16.6**: Configuração do GOOGLE_MAPS_API_KEY
- **16.7**: Configuração de credenciais S3
- **16.8**: Configuração de caminhos dos shapefiles
- **16.9**: Configuração de limites de upload
- **16.10**: Validação de variáveis obrigatórias

## Próximos Passos

1. Implementar migrações do Alembic (Task 2)
2. Criar scripts ETL para PRODES e DETER (Task 3)
3. Implementar serviços de integração (SICAR, Claude AI)
4. Implementar tarefas Celery para diagnósticos
5. Implementar geração de relatórios PDF

## Suporte

Para dúvidas ou problemas, consulte a documentação completa em `.kiro/specs/fazenda-ok-platform/`.
