"""
Gerenciamento de Sessão de Banco de Dados para a Plataforma FazendaOk.

Este módulo configura a conexão com o banco de dados PostgreSQL + PostGIS
usando SQLAlchemy com suporte assíncrono. Fornece o engine de banco de dados
e a função para obter sessões de banco de dados nas rotas da API.

Requisitos atendidos: 16.2
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# ============================================================================
# CONFIGURAÇÃO DO ENGINE DO BANCO DE DADOS
# ============================================================================

# Cria o motor (engine) assíncrono do SQLAlchemy
# Este engine gerencia o pool de conexões com o PostgreSQL
engine = create_async_engine(
    settings.database_url,  # URL de conexão carregada das variáveis de ambiente
    echo=False,  # Se True, loga todas as queries SQL (útil para debug)
    pool_pre_ping=True,  # Verifica conexões antes de usar (detecta conexões mortas)
    pool_size=10,  # Número de conexões mantidas no pool
    max_overflow=20,  # Número máximo de conexões extras além do pool_size
)

# ============================================================================
# CONFIGURAÇÃO DA FÁBRICA DE SESSÕES
# ============================================================================

# Cria a fábrica de sessões assíncronas
# Esta fábrica é usada para criar novas sessões de banco de dados
AsyncSessionLocal = async_sessionmaker(
    engine,  # Engine a ser usado
    class_=AsyncSession,  # Classe de sessão assíncrona
    expire_on_commit=False,  # Não expira objetos após commit (útil para acesso posterior)
)


# ============================================================================
# DEPENDENCY INJECTION PARA FASTAPI
# ============================================================================

async def obter_sessao_db() -> AsyncSession:
    """
    Obtém uma sessão do banco de dados para uso em endpoints FastAPI.
    
    Esta função é usada como dependency injection nos endpoints da API.
    Ela garante que a sessão seja fechada corretamente após o uso,
    mesmo em caso de exceções.
    
    Exemplo de uso:
        @app.get("/exemplo")
        async def exemplo(db: AsyncSession = Depends(obter_sessao_db)):
            resultado = await db.execute(select(Propriedade))
            return resultado.scalars().all()
    
    Yields:
        AsyncSession: Sessão assíncrona do banco de dados
    """
    async with AsyncSessionLocal() as sessao:
        try:
            yield sessao
        finally:
            # Garante que a sessão seja fechada, mesmo em caso de erro
            await sessao.close()
