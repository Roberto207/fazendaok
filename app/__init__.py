"""
FazendaOk Platform - Backend Application

Plataforma de diagnóstico de conformidade socioambiental para propriedades rurais brasileiras.

Este pacote contém toda a lógica do backend da Plataforma FazendaOk, incluindo:
- API REST construída com FastAPI
- Integração com banco de dados PostgreSQL + PostGIS
- Processamento assíncrono com Celery
- Análise espacial de dados de desmatamento (PRODES e DETER)
- Integração com APIs externas (SICAR, Claude AI, Google Maps)
- Upload e validação de fotos geotagueadas
- Geração de relatórios em PDF

Estrutura do pacote:
- api/: Endpoints da API REST
- models/: Modelos de dados SQLAlchemy
- schemas/: Schemas Pydantic para validação
- services/: Lógica de negócio e integrações externas
- tasks/: Tarefas assíncronas do Celery
- config.py: Configurações da aplicação
- main.py: Ponto de entrada da aplicação FastAPI

Requisitos atendidos: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10
"""

__version__ = "0.1.0"
__author__ = "FazendaOk Team"
