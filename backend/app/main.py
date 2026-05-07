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
from app.config import settings

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="FazendaOk Platform API",
    description=(
        "API REST para diagnóstico de conformidade socioambiental de propriedades rurais brasileiras.\n\n"
        "**Funcionalidades principais:**\n"
        "- Busca de propriedades pelo número CAR ou coordenadas GPS\n"
        "- Geração de diagnósticos cruzando dados de desmatamento (PRODES e DETER)\n"
        "- Upload e validação de fotos geotagueadas\n"
        "- Geração de relatórios em PDF\n"
        "- Histórico de diagnósticos\n\n"
        "**Tecnologias:**\n"
        "- FastAPI (framework web assíncrono)\n"
        "- PostgreSQL + PostGIS (banco de dados geoespacial)\n"
        "- Redis (cache e fila de tarefas)\n"
        "- Celery (processamento assíncrono)\n"
        "- Claude AI (explicações em linguagem natural)\n"
    ),
    version="0.1.0",
    docs_url="/docs",  # Documentação Swagger UI (Requisito 21.2)
    redoc_url="/redoc",  # Documentação ReDoc (Requisito 21.2)
    openapi_url="/openapi.json",  # Especificação OpenAPI 3.0 (Requisito 21.1)
    contact={
        "name": "FazendaOk Team",
        "email": "contato@fazendaok.com.br",
    },
    license_info={
        "name": "MIT",
    },
)

# ============================================================================
# CONFIGURAÇÃO DE MIDDLEWARES
# ============================================================================

# Middleware CORS - permite requisições do frontend (Requisito 21.3)
# Em produção, deve-se restringir allow_origins ao domínio específico do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Em produção, restringir ao domínio do frontend
    allow_credentials=True,  # Permite envio de cookies e credenciais
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permite todos os headers
)

# TODO: Adicionar middleware de rate limiting (Requisito 21.4)
# TODO: Adicionar middleware de logging de requisições (Requisito 21.4)
# TODO: Adicionar middleware de tratamento de erros (Requisito 21.4)

# ============================================================================
# REGISTRO DE ROTAS
# ============================================================================

# TODO: Incluir rotas da API v1 quando implementadas (Requisito 21.5)
# from app.api.v1 import router_v1
# app.include_router(router_v1, prefix="/api/v1", tags=["API v1"])

# ============================================================================
# EVENTOS DE CICLO DE VIDA
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação.
    
    Valida configurações e prepara recursos necessários.
    Requisito 21.6: Validar variáveis de ambiente na inicialização.
    """
    print("=" * 80)
    print("INICIANDO PLATAFORMA FAZENDAOK")
    print("=" * 80)
    print(f"Versão: {app.version}")
    print(f"Ambiente: {'Produção' if settings.database_url != 'postgresql+asyncpg://fazendaok:fazendaok@localhost:5432/fazendaok' else 'Desenvolvimento'}")
    print(f"Nível de log: {settings.log_level}")
    print(f"Documentação disponível em: /docs e /redoc")
    print("=" * 80)
    print()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação.
    
    Limpa recursos e fecha conexões.
    """
    print()
    print("=" * 80)
    print("ENCERRANDO PLATAFORMA FAZENDAOK")
    print("=" * 80)


# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get(
    "/",
    summary="Endpoint raiz da API",
    description="Retorna informações básicas sobre a API e links para documentação",
    tags=["Sistema"],
)
async def raiz():
    """
    Endpoint raiz da API.
    
    Retorna uma mensagem de boas-vindas e o status da API.
    Útil para verificar se o servidor está respondendo.
    
    Returns:
        dict: Informações sobre a API, status e links para documentação
    """
    return {
        "mensagem": "Bem-vindo à API da Plataforma FazendaOk",
        "descricao": "API para diagnóstico de conformidade socioambiental de propriedades rurais brasileiras",
        "status": "online",
        "versao": app.version,
        "documentacao": {
            "swagger_ui": f"{app.docs_url}",
            "redoc": f"{app.redoc_url}",
            "openapi_json": f"{app.openapi_url}",
        },
        "recursos": {
            "propriedades": "Busca de propriedades pelo CAR ou coordenadas",
            "diagnosticos": "Geração de diagnósticos de conformidade socioambiental",
            "fotos": "Upload e validação de fotos geotagueadas",
            "relatorios": "Geração de relatórios em PDF",
        },
    }


@app.get(
    "/saude",
    summary="Verificação de saúde da aplicação",
    description="Endpoint para verificar se a aplicação está funcionando corretamente",
    tags=["Sistema"],
)
async def verificar_saude():
    """
    Endpoint de verificação de saúde (health check).
    
    Verifica se a aplicação está funcionando corretamente.
    Este endpoint pode ser usado por load balancers e sistemas de monitoramento
    para verificar a disponibilidade do serviço.
    
    Returns:
        dict: Status de saúde da aplicação e componentes
    """
    # TODO: Adicionar verificação de conexão com banco de dados
    # TODO: Adicionar verificação de conexão com Redis
    # TODO: Adicionar verificação de status do Celery worker
    
    return {
        "status": "saudável",
        "servico": "FazendaOk Platform API",
        "versao": app.version,
        "componentes": {
            "api": "online",
            "banco_dados": "não verificado",  # TODO: implementar verificação
            "redis": "não verificado",  # TODO: implementar verificação
            "celery": "não verificado",  # TODO: implementar verificação
        },
    }


@app.get(
    "/info",
    summary="Informações sobre a aplicação",
    description="Retorna informações detalhadas sobre configuração e recursos disponíveis",
    tags=["Sistema"],
)
async def informacoes():
    """
    Endpoint de informações sobre a aplicação.
    
    Retorna informações sobre configuração (sem expor dados sensíveis)
    e recursos disponíveis.
    
    Returns:
        dict: Informações sobre configuração e recursos
    """
    return {
        "aplicacao": {
            "nome": app.title,
            "versao": app.version,
            "descricao": "Plataforma de diagnóstico de conformidade socioambiental",
        },
        "configuracao": {
            "max_foto_size_mb": settings.max_foto_size_mb,
            "max_fotos_por_upload": settings.max_fotos_por_upload,
            "rate_limit_per_hour": settings.rate_limit_per_hour,
            "diagnostic_cache_ttl_hours": settings.diagnostic_cache_ttl_seconds / 3600,
        },
        "integracao": {
            "sicar_disponivel": bool(settings.infosimples_token),
            "claude_ai_disponivel": bool(settings.anthropic_api_key),
            "google_maps_disponivel": bool(settings.google_maps_api_key),
            "s3_disponivel": bool(settings.aws_access_key_id and settings.aws_secret_access_key),
        },
        "dados_etl": {
            "prodes_configurado": bool(settings.prodes_shapefile_path),
            "deter_configurado": bool(settings.deter_shapefile_path),
        },
    }
