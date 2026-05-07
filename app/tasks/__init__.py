"""
Tarefas do Celery para a Plataforma FazendaOk.
"""

from app.tasks.photo_tasks import processar_tarefa_foto

__all__ = ["processar_tarefa_foto"]
