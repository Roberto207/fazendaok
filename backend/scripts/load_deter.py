"""
Script de ETL para carregar dados do DETER Cerrado no banco de dados.
Transforma os dados do shapefile e insere na tabela deter_cerrado.
Requisitos atendidos: 3.2, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7
"""

import os
import asyncio
import geopandas as gpd
import logging
import sys
from datetime import datetime, timedelta

# Adiciona o diretório atual ao sys.path para importar módulos da app
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.deter import DeterCerrado
from app.config import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("load_deter")

async def carregar_deter():
    """
    Lê o shapefile do DETER, filtra por data e insere no PostGIS.
    """
    path = settings.deter_shapefile_path
    
    if not path or not os.path.exists(path):
        logger.error(f"Shapefile do DETER não encontrado no caminho: {path}")
        return

    try:
        logger.info(f"Lendo shapefile DETER: {path}")
        gdf = gpd.read_file(path, engine="pyogrio")
        
        # 1. Garantir CRS EPSG:4326 (WGS84)
        if gdf.crs != "EPSG:4326":
            logger.info(f"Reprojetando de {gdf.crs} para EPSG:4326")
            gdf = gdf.to_crs("EPSG:4326")

        # 2. Filtrar dados (Últimos 24 meses)
        possible_date_cols = ['VIEW_DATE', 'date', 'data', 'VIEW_DATA', 'VIEW_DAT']
        date_col = next((c for c in possible_date_cols if c in gdf.columns), None)
        
        if date_col:
            # Converte para datetime se necessário
            import pandas as pd
            gdf[date_col] = pd.to_datetime(gdf[date_col])
            limite_data = datetime.now() - timedelta(days=730)
            logger.info(f"Filtrando alertas a partir de {limite_data.date()}")
            gdf = gdf[gdf[date_col] >= limite_data]
        else:
            logger.warning("Coluna de data não encontrada. Importando todos os registros.")

        total = len(gdf)
        logger.info(f"Total de registros a serem importados: {total}")
        
        # 3. Inserção em lotes
        batch_size = 100
        async with AsyncSessionLocal() as session:
            for i in range(0, total, batch_size):
                batch_gdf = gdf.iloc[i : i + batch_size]
                
                for _, row in batch_gdf.iterrows():
                    wkt_geom = row.geometry.wkt
                    
                    # Identifica a área
                    area_ha = 0.0
                    area_cols = ['area_ha', 'area', 'AREA']
                    area_col = next((c for c in area_cols if c in row), None)
                    if area_col:
                        area_ha = float(row[area_col])

                    objeto = DeterCerrado(
                        geometry=f"SRID=4326;{wkt_geom}",
                        alert_date=row[date_col].date() if date_col else datetime.now().date(),
                        area_ha=area_ha,
                        source_metadata=row.drop('geometry').to_dict()
                    )
                    session.add(objeto)
                
                await session.commit()
                logger.info(f"Processado: {min(i + batch_size, total)}/{total}")

        logger.info("Importação do DETER concluída com sucesso!")

    except Exception as e:
        logger.error(f"Erro durante a importação do DETER: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(carregar_deter())
