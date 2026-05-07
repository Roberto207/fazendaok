"""
Aplicação Principal FastAPI para a Plataforma FazendaOk.

Este módulo inicializa a aplicação FastAPI, configura middlewares,
registra rotas e define endpoints básicos de verificação.

A Plataforma FazendaOk é um sistema de diagnóstico de conformidade
socioambiental para propriedades rurais brasileiras, cruzando dados
do CAR com bases de desmatamento (PRODES e DETER).

Requisitos atendidos: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router_v1
from app.config import settings

# Inicialização da aplicação FastAPI com metadados
app = FastAPI(
    title="FazendaOk Platform API",
    description=(
        "API REST para diagnóstico de conformidade socioambiental de propriedades rurais. "
        "Permite buscar propriedades pelo CAR, gerar diagnósticos cruzando dados de "
        "desmatamento (PRODES e DETER), fazer upload de fotos geotagueadas e gerar "
        "relatórios em PDF."
    ),
    version="0.1.0",
    docs_url="/docs",  # Documentação Swagger UI
    redoc_url="/redoc",  # Documentação ReDoc
)

# ============================================================================
# CONFIGURAÇÃO DE MIDDLEWARES
# ============================================================================

# Middleware CORS - permite requisições do frontend
# Em produção, deve-se restringir allow_origins ao domínio específico do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Em produção, restringir ao domínio do frontend
    allow_credentials=True,  # Permite envio de cookies e credenciais
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permite todos os headers
)

# ============================================================================
# REGISTRO DE ROTAS
# ============================================================================

# Inclusão do roteador da API v1 com prefixo /api/v1
# Todas as rotas da API estarão disponíveis em /api/v1/*
app.include_router(router_v1, prefix="/api/v1")


# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/")
async def raiz():
    """
    Endpoint raiz da API.
    
    Retorna uma mensagem de boas-vindas e o status da API.
    Útil para verificar se o servidor está respondendo.
    
    Returns:
        dict: Mensagem de boas-vindas e status online
    """
    return {
        "mensagem": "Bem-vindo à API da Plataforma FazendaOk",
        "descricao": "API para diagnóstico de conformidade socioambiental de propriedades rurais",
        "status": "online",
        "versao": "0.1.0",
        "documentacao": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/saude")
async def verificar_saude():
    """
    Endpoint de verificação de saúde (health check).
    
    Verifica se a aplicação está funcionando corretamente.
    Este endpoint pode ser usado por load balancers e sistemas de monitoramento
    para verificar a disponibilidade do serviço.
    
    Returns:
        dict: Status de saúde da aplicação
    """
    return {
        "status": "saudável",
        "servico": "FazendaOk Platform API"
    }
