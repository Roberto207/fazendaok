"""
Endpoints de API para busca e gerenciamento de propriedades.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape

from app.database import obter_sessao_db
from app.models.property import Propriedade
from app.services.sicar_service import ServicoSICAR
from app.schemas.property import (
    PedidoBuscaPorCAR, 
    PedidoBuscaPorCoordenadas, 
    PedidoBuscaPorEndereco, 
    RespostaPropriedade
)

router = APIRouter()


@router.post("/buscar/car", response_model=RespostaPropriedade)
async def buscar_por_car(
    pedido: PedidoBuscaPorCAR,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """
    Busca uma propriedade pelo número do CAR.
    Verifica primeiro no banco de dados local; se não encontrar, consulta o SICAR.
    """
    # 1. Verifica no banco de dados local
    resultado = await db.execute(
        select(Propriedade).where(Propriedade.car_number == pedido.numero_car)
    )
    propriedade = resultado.scalar_one_or_none()
    
    if propriedade:
        return _converter_para_resposta(propriedade)
    
    # 2. Se não encontrar localmente, busca no SICAR
    servico_sicar = ServicoSICAR()
    dados_sicar = await servico_sicar.buscar_propriedade_por_car(pedido.numero_car)
    
    if not dados_sicar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propriedade com CAR {pedido.numero_car} não encontrada no SICAR."
        )
    
    # 3. Salva a nova propriedade no banco de dados
    try:
        # Converte GeoJSON para geometria Shapely e depois para GeoAlchemy2
        geometria_shapely = shape(dados_sicar["geometria_geojson"])
        geometria_geoa = from_shape(geometria_shapely, srid=4326)
        
        nova_propriedade = Propriedade(
            car_number=dados_sicar["numero_car"],
            polygon=geometria_geoa,
            total_area_ha=dados_sicar["area_total_ha"],
            app_area_ha=dados_sicar.get("area_app_ha"),
            legal_reserve_area_ha=dados_sicar.get("area_reserva_legal_ha"),
            car_status=dados_sicar["status_car"],
            dados_adicionais=dados_sicar.get("dados_adicionais")
        )
        
        db.add(nova_propriedade)
        await db.commit()
        await db.refresh(nova_propriedade)
        
        return _converter_para_resposta(nova_propriedade)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar e salvar dados da propriedade: {str(e)}"
        )


@router.post("/buscar/coordenadas", response_model=RespostaPropriedade)
async def buscar_por_coordenadas(
    pedido: PedidoBuscaPorCoordenadas,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """
    Busca uma propriedade pelas coordenadas geográficas.
    """
    # 1. Busca localmente por intersecção espacial
    ponto_wkt = f"POINT({pedido.longitude} {pedido.latitude})"
    ponto_geoa = WKTElement(ponto_wkt, srid=4326)
    
    # Busca propriedade que contém o ponto (ST_Contains)
    from sqlalchemy import func
    resultado = await db.execute(
        select(Propriedade).where(func.ST_Contains(Propriedade.polygon, ponto_geoa))
    )
    propriedade = resultado.scalar_one_or_none()
    
    if propriedade:
        return _converter_para_resposta(propriedade)
    
    # 2. Se não encontrar localmente, tenta buscar via serviço externo
    servico_sicar = ServicoSICAR()
    propriedades_prox = await servico_sicar.buscar_propriedades_por_coordenadas(
        pedido.latitude, pedido.longitude
    )
    
    if not propriedades_prox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma propriedade encontrada para estas coordenadas."
        )
    
    # Por simplicidade, pega a primeira encontrada e processa como busca por CAR
    # (reaproveitando a lógica de salvamento)
    primeira = propriedades_prox[0]
    return await buscar_por_car(PedidoBuscaPorCAR(numero_car=primeira["numero_car"]), db)


@router.post("/buscar/endereco", response_model=RespostaPropriedade)
async def buscar_por_endereco(
    pedido: PedidoBuscaPorEndereco,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """
    Busca uma propriedade por endereço (usando Google Places).
    """
    # TODO: Implementar Geocoding do Google
    # Por enquanto, retorna erro de não implementado
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Busca por endereço ainda não implementada. Use busca por CAR ou Coordenadas."
    )


def _converter_para_resposta(propriedade: Propriedade) -> RespostaPropriedade:
    """Helper para converter o modelo do banco de dados para o esquema de resposta."""
    # Converte geometria PostGIS para GeoJSON
    geometria_shapely = to_shape(propriedade.polygon)
    from shapely.geometry import mapping
    
    return RespostaPropriedade(
        id=str(propriedade.id),
        numero_car=propriedade.car_number,
        area_total_ha=propriedade.total_area_ha,
        area_app_ha=propriedade.app_area_ha,
        area_reserva_legal_ha=propriedade.legal_reserve_area_ha,
        status_car=propriedade.car_status,
        poligono_geojson=mapping(geometria_shapely),
        dados_adicionais=propriedade.dados_adicionais,
        data_criacao=propriedade.created_at.isoformat()
    )
