"""
Pacote Principal da Aplicação FazendaOk Platform.

Este pacote contém toda a lógica da aplicação backend, incluindo:
- API REST (FastAPI)
- Modelos de banco de dados (SQLAlchemy + PostGIS)
- Serviços de negócio
- Tarefas assíncronas (Celery)
- Schemas de validação (Pydantic)

A Plataforma FazendaOk permite verificar a conformidade socioambiental
de propriedades rurais brasileiras cruzando dados do CAR com bases de
desmatamento (PRODES e DETER do INPE).

Requisitos atendidos: Task 1 - Backend project structure and core configuration
"""

__version__ = "0.1.0"
__author__ = "FazendaOk Team"
__description__ = "Plataforma de diagnóstico de conformidade socioambiental para propriedades rurais"
