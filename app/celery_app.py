"""
Configuração da Aplicação Celery para a Plataforma FazendaOk.

Este módulo configura o Celery para processamento assíncrono de tarefas,
usando Redis como message broker e backend de resultados.

O Celery é usado para processar tarefas demoradas de forma assíncrona:
- Geração de diagnósticos (análise espacial + IA)
- Processamento de fotos (extração EXIF + validação + upload S3)

Requisitos atendidos: 18.1, 18.5, 18.6, 18.7
"""

from celery import Celery
from app.config import settings

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO CELERY
# ============================================================================

# Inicializa a aplicação Celery
celery_app = Celery(
    "fazendaok",  # Nome da aplicação
    broker=settings.redis_url,  # Redis como message broker (fila de tarefas)
    backend=settings.redis_url,  # Redis como backend de resultados
    include=[
        "app.tasks.photo_tasks",
        "app.tasks.diagnostic_tasks"
    ]  # Módulos de tarefas a serem importados
)

# ============================================================================
# CONFIGURAÇÃO DO CELERY
# ============================================================================

celery_app.conf.update(
    # Serialização de tarefas e resultados
    task_serializer="json",  # Serializa tarefas como JSON
    accept_content=["json"],  # Aceita apenas conteúdo JSON (segurança)
    result_serializer="json",  # Serializa resultados como JSON
    
    # Configuração de timezone
    timezone="America/Sao_Paulo",  # Timezone do Brasil
    enable_utc=True,  # Usa UTC internamente
    
    # Rastreamento de tarefas
    task_track_started=True,  # Rastreia quando tarefas iniciam
    
    # Limites de tempo
    task_time_limit=300,  # Limite rígido: 5 minutos (mata a tarefa)
    task_soft_time_limit=240,  # Limite suave: 4 minutos (lança exceção)
    
    # Expiração de resultados
    result_expires=86400,  # Resultados expiram após 24 horas
    
    # Configuração de workers
    task_acks_late=True,  # Confirma tarefa apenas após conclusão (não antes)
    worker_prefetch_multiplier=1,  # Worker pega 1 tarefa por vez (evita sobrecarga)
    
    # Configuração de retry (tentativas em caso de falha)
    task_default_retry_delay=60,  # Aguarda 1 minuto antes de tentar novamente
    task_max_retries=3,  # Máximo de 3 tentativas em caso de falha
)
