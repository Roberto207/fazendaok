"""
Gerenciamento de Configuração para a Plataforma FazendaOk.

Este módulo carrega todas as configurações da aplicação a partir de variáveis
de ambiente usando pydantic-settings. Todas as configurações sensíveis devem
ser definidas no arquivo .env e nunca commitadas no repositório.

Requisitos atendidos: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    
    Esta classe define todas as configurações necessárias para o funcionamento
    da plataforma FazendaOk, incluindo conexões com banco de dados, APIs externas,
    armazenamento S3, e parâmetros de configuração da aplicação.
    
    Todas as variáveis podem ser definidas no arquivo .env ou como variáveis
    de ambiente do sistema. Valores padrão são fornecidos quando apropriado.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",  # Arquivo de onde carregar as variáveis
        env_file_encoding="utf-8",  # Codificação do arquivo
        case_sensitive=False,  # Permite variáveis em qualquer case
        extra="ignore"  # Ignora variáveis extras não definidas
    )
    
    # ========================================================================
    # BANCO DE DADOS
    # ========================================================================
    
    database_url: str = "postgresql+asyncpg://fazendaok:fazendaok@localhost:5432/fazendaok"
    """
    URL de conexão com o banco de dados PostgreSQL com PostGIS.
    Formato: postgresql+asyncpg://usuario:senha@host:porta/nome_banco
    Requisito: 16.2
    """
    
    # ========================================================================
    # REDIS (Cache e Fila de Tarefas)
    # ========================================================================
    
    redis_url: str = "redis://localhost:6379/0"
    """
    URL de conexão com o servidor Redis.
    Usado para cache de diagnósticos e como broker do Celery.
    Formato: redis://host:porta/database_number
    Requisito: 16.3
    """
    
    # ========================================================================
    # APIs EXTERNAS
    # ========================================================================
    
    infosimples_token: Optional[str] = None
    """
    Token de autenticação para a API da Infosimples (acesso ao SICAR).
    Obrigatório para buscar dados de propriedades do CAR.
    Requisito: 16.4
    """
    
    anthropic_api_key: Optional[str] = None
    """
    Chave de API da Anthropic para acesso ao Claude AI.
    Usado para gerar explicações em linguagem natural dos diagnósticos.
    Formato: sk-ant-...
    Requisito: 16.5
    """
    
    google_maps_api_key: Optional[str] = None
    """
    Chave de API do Google Maps.
    Usado para busca de endereços, mapas interativos e mapas estáticos em PDFs.
    Formato: AIza...
    Requisito: 16.6
    """
    
    # ========================================================================
    # ARMAZENAMENTO S3 (Fotos)
    # ========================================================================
    
    aws_bucket_name: str = "fazendaok-photos"
    """
    Nome do bucket S3 (ou compatível) para armazenar fotos.
    Requisito: 16.7
    """
    
    aws_access_key_id: Optional[str] = None
    """
    Access Key ID para autenticação no S3.
    Requisito: 16.7
    """
    
    aws_secret_access_key: Optional[str] = None
    """
    Secret Access Key para autenticação no S3.
    Requisito: 16.7
    """
    
    aws_endpoint_url: Optional[str] = None
    """
    URL do endpoint S3 (para serviços compatíveis como MinIO).
    Para AWS S3 padrão, deixar como None.
    Exemplo: https://s3.amazonaws.com ou http://localhost:9000
    Requisito: 16.7
    """
    
    # ========================================================================
    # CAMINHOS DOS DADOS ETL (Shapefiles)
    # ========================================================================
    
    prodes_shapefile_path: Optional[str] = None
    """
    Caminho completo para o shapefile do PRODES Cerrado.
    Usado pelo script de ETL para carregar dados de desmatamento.
    Exemplo: /data/prodes_cerrado.shp
    Requisito: 16.8
    """
    
    deter_shapefile_path: Optional[str] = None
    """
    Caminho completo para o shapefile do DETER Cerrado.
    Usado pelo script de ETL para carregar alertas de desmatamento.
    Exemplo: /data/deter_cerrado.shp
    Requisito: 16.8
    """
    
    # ========================================================================
    # CONFIGURAÇÕES DA APLICAÇÃO
    # ========================================================================
    
    max_foto_size_mb: int = 10
    """
    Tamanho máximo permitido para upload de fotos (em megabytes).
    Padrão: 10 MB
    Requisito: 16.9
    """
    
    max_fotos_por_upload: int = 20
    """
    Número máximo de fotos permitidas em um único upload.
    Padrão: 20 fotos
    Requisito: 16.9
    """
    
    log_level: str = "INFO"
    """
    Nível de log da aplicação.
    Valores possíveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
    Padrão: INFO
    """
    
    rate_limit_per_hour: int = 100
    """
    Limite de requisições por hora por endereço IP.
    Usado para prevenir abuso da API.
    Padrão: 100 requisições/hora
    """
    
    # ========================================================================
    # CACHE
    # ========================================================================
    
    diagnostic_cache_ttl_seconds: int = 21600
    """
    Tempo de vida (TTL) do cache de diagnósticos no Redis.
    Padrão: 21600 segundos (6 horas)
    """
    
    # ========================================================================
    # UPLOAD
    # ========================================================================
    
    upload_temp_dir: str = "/tmp/fazendaok/uploads"
    """
    Diretório temporário para armazenar uploads antes do processamento.
    """


# Instância global de configurações
# Esta instância é importada por toda a aplicação para acessar as configurações
settings = Settings()
