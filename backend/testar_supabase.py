import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

async def testar_conexao():
    """
    Testa a conexão com o banco de dados (Supabase) usando SQLAlchemy assíncrono.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERRO: DATABASE_URL não encontrada no arquivo .env")
        sys.exit(1)
        
    print(f"Tentando conectar com: {database_url.replace(database_url.split('@')[0].split('//')[1], '***:***')}")
    
    try:
        # Criar engine assíncrona
        engine = create_async_engine(database_url, echo=False)
        
        # Tentar conectar e executar uma query simples
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            
            print("\n✅ CONEXÃO BEM SUCEDIDA!")
            print(f"Versão do PostgreSQL (Supabase): {version}")
            
        # Fechar a engine
        await engine.dispose()
        
    except Exception as e:
        print("\n❌ FALHA NA CONEXÃO!")
        print(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Iniciando teste de conexão com o banco de dados...")
    asyncio.run(testar_conexao())
