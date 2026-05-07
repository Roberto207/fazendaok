# Migrações de Banco de Dados - Alembic

## Visão Geral

Este diretório contém a configuração do Alembic para gerenciar migrações do banco de dados PostgreSQL + PostGIS da Plataforma FazendaOk.

O Alembic está configurado para trabalhar com SQLAlchemy assíncrono e suporta operações geoespaciais através do PostGIS.

## Estrutura

```
backend/alembic/
├── env.py              # Configuração do ambiente de migração (assíncrono)
├── script.py.mako      # Template para novos scripts de migração
└── versions/           # Diretório com os scripts de migração
```

## Comandos Principais

### Criar uma Nova Migração

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Criar migração com autogenerate (detecta mudanças nos modelos)
alembic revision --autogenerate -m "Descrição da migração"

# Criar migração vazia (para operações manuais)
alembic revision -m "Descrição da migração"
```

### Aplicar Migrações

```bash
# Aplicar todas as migrações pendentes
alembic upgrade head

# Aplicar uma migração específica
alembic upgrade <revision_id>

# Aplicar próxima migração
alembic upgrade +1
```

### Reverter Migrações

```bash
# Reverter última migração
alembic downgrade -1

# Reverter para uma revisão específica
alembic downgrade <revision_id>

# Reverter todas as migrações
alembic downgrade base
```

### Verificar Status

```bash
# Ver histórico de migrações
alembic history

# Ver migração atual
alembic current

# Verificar se há diferenças entre modelos e banco
alembic check
```

## Configuração

### Variáveis de Ambiente

O Alembic carrega automaticamente a URL do banco de dados de `app/config.py`, que por sua vez lê a variável de ambiente `DATABASE_URL`.

Certifique-se de que o arquivo `.env` contém:

```bash
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/fazendaok
```

### Modelos SQLAlchemy

Para que o autogenerate funcione corretamente, todos os modelos devem:

1. Herdar de `app.models.base.Base`
2. Ser importados em `app/models/__init__.py`
3. Estar importados antes de executar o Alembic

O arquivo `env.py` já está configurado para importar automaticamente todos os modelos.

## Características Especiais

### Suporte Assíncrono

Esta configuração usa SQLAlchemy assíncrono com asyncpg. As migrações são executadas de forma assíncrona, o que é compatível com o resto da aplicação.

### Suporte PostGIS

O Alembic está configurado para trabalhar com tipos geométricos do PostGIS:

- `Geometry(Polygon, 4326)` para polígonos de propriedades
- `Geometry(Point, 4326)` para coordenadas GPS de fotos
- Índices espaciais (GIST) para otimização de queries

### Comparação de Tipos

A configuração inclui:

- `compare_type=True`: Detecta mudanças em tipos de colunas
- `compare_server_default=True`: Detecta mudanças em valores padrão

## Exemplo de Migração

```python
"""Adicionar coluna de status à tabela propriedades

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-15 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Identificadores de revisão usados pelo Alembic
revision: str = 'abc123'
down_revision: Union[str, Sequence[str], None] = 'xyz789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplicar mudanças ao banco de dados."""
    op.add_column('propriedades', 
        sa.Column('status', sa.String(50), nullable=True)
    )


def downgrade() -> None:
    """Reverter mudanças do banco de dados."""
    op.drop_column('propriedades', 'status')
```

## Requisitos Atendidos

Esta configuração atende aos seguintes requisitos:

- **17.1**: Uso do Alembic para gerenciamento de migrações
- **17.2**: Scripts de migração para todas as mudanças de schema
- **17.7**: Registro de versões de migração na tabela alembic_version

## Troubleshooting

### Erro de Conexão

Se você receber erro de conexão ao executar comandos do Alembic:

1. Verifique se o PostgreSQL está rodando
2. Verifique se a variável `DATABASE_URL` está correta no `.env`
3. Verifique se o banco de dados existe

### Autogenerate Não Detecta Mudanças

Se o autogenerate não detectar mudanças nos modelos:

1. Verifique se o modelo herda de `Base`
2. Verifique se o modelo está importado em `app/models/__init__.py`
3. Verifique se não há erros de sintaxe nos modelos

### Conflitos de Migração

Se houver conflitos entre migrações:

```bash
# Ver histórico de migrações
alembic history

# Mesclar branches de migração
alembic merge -m "Mesclar branches" <rev1> <rev2>
```

## Referências

- [Documentação do Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostGIS](https://postgis.net/)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)