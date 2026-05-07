"""initial_schema

Revision ID: 25a93a57259e
Revises: 
Create Date: 2026-05-07 00:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '25a93a57259e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Habilitar PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # 2. Tabela Propriedades
    op.create_table(
        'propriedades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('car_number', sa.String(), nullable=False),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('municipality', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('area_ha', sa.Float(), nullable=True),
        sa.Column('car_status', sa.String(), nullable=True),
        sa.Column('polygon', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('car_number')
    )
    op.create_index('idx_propriedades_car_number', 'propriedades', ['car_number'], unique=True)

    # 3. Tabela Diagnosticos
    op.create_table(
        'diagnosticos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('prodes_overlap_area_ha', sa.Float(), nullable=True),
        sa.Column('deter_alert_count', sa.Integer(), nullable=True),
        sa.Column('latest_deter_date', sa.Date(), nullable=True),
        sa.Column('prodes_intersections', sa.JSON(), nullable=True),
        sa.Column('deter_intersections', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['property_id'], ['propriedades.id'], )
    )
    op.create_index('idx_diagnosticos_property_id', 'diagnosticos', ['property_id'])

    # 4. Tabela Fotos
    op.create_table(
        'fotos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('diagnostic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('s3_url', sa.String(), nullable=True),
        sa.Column('thumbnail_s3_url', sa.String(), nullable=True),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('gps_point', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('validation_status', sa.String(), nullable=False),
        sa.Column('capture_date', sa.DateTime(), nullable=True),
        sa.Column('exif_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['diagnostic_id'], ['diagnosticos.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['propriedades.id'], )
    )

    # 5. Tabela ProdesCerrado
    op.create_table(
        'prodes_cerrado',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('area_ha', sa.Float(), nullable=False),
        sa.Column('source_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_prodes_cerrado_year', 'prodes_cerrado', ['year'])

    # 6. Tabela DeterCerrado
    op.create_table(
        'deter_cerrado',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('alert_date', sa.Date(), nullable=False),
        sa.Column('area_ha', sa.Float(), nullable=False),
        sa.Column('source_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_deter_cerrado_alert_date', 'deter_cerrado', ['alert_date'])


def downgrade() -> None:
    op.drop_table('deter_cerrado')
    op.drop_table('prodes_cerrado')
    op.drop_table('fotos')
    op.drop_table('diagnosticos')
    op.drop_table('propriedades')
