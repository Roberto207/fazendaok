"""
Script de ETL para carregar dados do PRODES Cerrado no banco de dados.
Transforma os dados do shapefile e insere na tabela prodes_cerrado.
Requisitos atendidos: 3.1, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
"""

import os
import asyncio
import geopandas as gpd
import logging
import sys
from sqlalchemy import text

# Adiciona o diretório atual ao sys.path para importar módulos da app
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.prodes import ProdesCerrado
from app.config import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("load_prodes")

async def carregar_prodes():
    """
    Lê o shapefile do PRODES, filtra por ano e insere no PostGIS.
    """
    path = settings.prodes_shapefile_path
    
    if not path or not os.path.exists(path):
        logger.error(f"Shapefile do PRODES não encontrado no caminho: {path}")
        logger.info("Certifique-se de que o arquivo existe e o caminho no .env está correto.")
        return

    try:
        logger.info(f"Lendo shapefile PRODES: {path}")
        # Usa pyogrio se disponível para performance, caso contrário fiona
        gdf = gpd.read_file(path, engine="pyogrio")
        
        # 1. Garantir CRS EPSG:4326 (WGS84)
        if gdf.crs != "EPSG:4326":
            logger.info(f"Reprojetando de {gdf.crs} para EPSG:4326")
            gdf = gdf.to_crs("EPSG:4326")

        # 2. Filtrar dados (Ano >= 2019)
        # Os nomes das colunas podem variar (ano, year, YEAR, ANO)
        possible_year_cols = ['ano', 'year', 'YEAR', 'ANO']
        year_col = next((c for c in possible_year_cols if c in gdf.columns), None)
        
        if year_col:
            logger.info(f"Filtrando por ano >= 2019 usando coluna '{year_col}'")
            gdf = gdf[gdf[year_col] >= 2019]
        else:
            logger.warning("Coluna de ano não encontrada. Importando todos os registros.")

        total = len(gdf)
        logger.info(f"Total de registros a serem importados: {total}")
        
        # 3. Inserção em lotes
        batch_size = 100
        async with AsyncSessionLocal() as session:
            for i in range(0, total, batch_size):
                batch_gdf = gdf.iloc[i : i + batch_size]
                
                for _, row in batch_gdf.iterrows():
                    # Converte a geometria para string WKT
                    # O GeoAlchemy2 aceita WKT com SRID prefixado ou via funções ST
                    wkt_geom = row.geometry.wkt
                    
                    # Tenta identificar a área
                    area_ha = 0.0
                    area_cols = ['area_ha', 'area', 'AREA', 'area_km2']
                    area_col = next((c for c in area_cols if c in row), None)
                    if area_col:
                        area_ha = float(row[area_col])
                        if 'km2' in area_col.lower():
                            area_ha *= 100.0 # Converte km2 para ha

                    objeto = ProdesCerrado(
                        geometry=f"SRID=4326;{wkt_geom}",
                        year=int(row[year_col]) if year_col else 0,
                        area_ha=area_ha,
                        source_metadata=row.drop('geometry').to_dict()
                    )
                    session.add(objeto)
                
                await session.commit()
                logger.info(f"Processado: {min(i + batch_size, total)}/{total}")

        logger.info("Importação do PRODES concluída com sucesso!")

    except Exception as e:
        logger.error(f"Erro durante a importação do PRODES: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(carregar_prodes())
