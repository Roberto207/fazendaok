"""
Serviço para operações espaciais e geométricas na Plataforma FazendaOk.
Utiliza Shapely para manipulação de geometrias.
"""

from shapely.geometry import shape, Point, Polygon
from shapely.validation import make_valid
from typing import Dict, Any, Optional, List


class ServicoEspacial:
    """Serviço que fornece funções utilitárias para cálculos geográficos."""

    @staticmethod
    def validar_geometria(geojson: Dict[str, Any]) -> Any:
        """
        Converte GeoJSON para objeto Shapely e garante que seja uma geometria válida.
        """
        geometria = shape(geojson)
        if not geometria.is_valid:
            geometria = make_valid(geometria)
        return geometria

    @staticmethod
    def ponto_dentro_poligono(lat: float, lon: float, poligono_geojson: Dict[str, Any]) -> bool:
        """
        Verifica se um ponto (lat, lon) está dentro de um polígono.
        """
        ponto = Point(lon, lat)  # Shapely usa (x, y) -> (lon, lat)
        poligono = ServicoEspacial.validar_geometria(poligono_geojson)
        return poligono.contains(ponto)

    @staticmethod
    def calcular_area_interseccao(geom1_geojson: Dict[str, Any], geom2_geojson: Dict[str, Any]) -> float:
        """
        Calcula a área de intersecção entre duas geometrias (em unidades da geometria).
        Nota: Para áreas precisas em hectares, as geometrias devem estar em um sistema de coordenadas projetado.
        Esta implementação assume que as geometrias podem ser convertidas e intersectadas.
        """
        g1 = ServicoEspacial.validar_geometria(geom1_geojson)
        g2 = ServicoEspacial.validar_geometria(geom2_geojson)
        
        if not g1.intersects(g2):
            return 0.0
            
        interseccao = g1.intersection(g2)
        return interseccao.area

    @staticmethod
    def calcular_percentual_sobreposicao(alvo_geojson: Dict[str, Any], camada_geojson: Dict[str, Any]) -> float:
        """
        Calcula o percentual da área 'alvo' que é sobreposta pela 'camada'.
        """
        alvo = ServicoEspacial.validar_geometria(alvo_geojson)
        camada = ServicoEspacial.validar_geometria(camada_geojson)
        
        area_alvo = alvo.area
        if area_alvo == 0:
            return 0.0
            
        if not alvo.intersects(camada):
            return 0.0
            
        interseccao = alvo.intersection(camada)
        return (interseccao.area / area_alvo) * 100.0

    @staticmethod
    async def buscar_interseccoes_prodes(db, poligono_wkb) -> List[Dict[str, Any]]:
        """
        Busca intersecções com a base PRODES usando PostGIS.
        """
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                ST_AsGeoJSON(ST_Intersection(geometry, :poligono)) as geojson,
                ST_Area(ST_Intersection(geometry, :poligono)::geography) / 10000.0 as area_ha,
                year
            FROM prodes_cerrado
            WHERE ST_Intersects(geometry, :poligono)
            AND year >= 2019
        """)
        
        result = await db.execute(query, {"poligono": poligono_wkb})
        return [dict(row._mapping) for row in result]

    @staticmethod
    async def buscar_interseccoes_deter(db, poligono_wkb) -> List[Dict[str, Any]]:
        """
        Busca intersecções com a base DETER usando PostGIS.
        """
        from sqlalchemy import text
        from datetime import date, timedelta
        
        limite_data = date.today() - timedelta(days=730)  # Últimos 24 meses
        
        query = text("""
            SELECT 
                ST_AsGeoJSON(ST_Intersection(geometry, :poligono)) as geojson,
                ST_Area(ST_Intersection(geometry, :poligono)::geography) / 10000.0 as area_ha,
                alert_date
            FROM deter_cerrado
            WHERE ST_Intersects(geometry, :poligono)
            AND alert_date >= :limite_data
        """)
        
        result = await db.execute(query, {"poligono": poligono_wkb, "limite_data": limite_data})
        return [dict(row._mapping) for row in result]
