"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# ============================================================================
# IDENTIFICADORES DE REVISÃO
# ============================================================================

# Identificador único desta migração
revision: str = ${repr(up_revision)}

# Migração anterior (None se for a primeira)
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}

# Labels de branch (usado para ramificações de migração)
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}

# Dependências de outras migrações
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


# ============================================================================
# FUNÇÕES DE MIGRAÇÃO
# ============================================================================

def upgrade() -> None:
    """
    Aplica as mudanças desta migração ao banco de dados.
    
    Esta função é executada quando você roda:
    - alembic upgrade head
    - alembic upgrade +1
    - alembic upgrade <revision_id>
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Reverte as mudanças desta migração do banco de dados.
    
    Esta função é executada quando você roda:
    - alembic downgrade -1
    - alembic downgrade <revision_id>
    - alembic downgrade base
    """
    ${downgrades if downgrades else "pass"}
