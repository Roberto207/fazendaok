"""
Testes de integração para validadores com schemas Pydantic.

Este módulo verifica se as funções de validação puras estão
corretamente integradas com os schemas Pydantic.
"""

import pytest
from pydantic import ValidationError

from app.schemas.property import PedidoBuscaPorCAR, PedidoBuscaPorCoordenadas


def test_schema_car_valido_aceito():
    """
    Testa se o schema Pydantic aceita números CAR válidos.
    """
    # Número CAR válido
    pedido = PedidoBuscaPorCAR(numero_car="GO-5208707-ABCD1234EFGH5678")
    assert pedido.numero_car == "GO-5208707-ABCD1234EFGH5678"


def test_schema_car_invalido_rejeitado():
    """
    Testa se o schema Pydantic rejeita números CAR inválidos.
    """
    # Número CAR inválido (letras minúsculas)
    with pytest.raises(ValidationError) as exc_info:
        PedidoBuscaPorCAR(numero_car="go-5208707-abcd1234efgh5678")
    
    # Verifica se a mensagem de erro está correta
    assert "Formato de CAR inválido" in str(exc_info.value)


def test_schema_car_sem_separadores_rejeitado():
    """
    Testa se o schema Pydantic rejeita números CAR sem separadores.
    """
    with pytest.raises(ValidationError):
        PedidoBuscaPorCAR(numero_car="GO5208707ABCD1234EFGH5678")


def test_schema_coordenadas_validas_aceitas():
    """
    Testa se o schema Pydantic aceita coordenadas válidas.
    """
    # Coordenadas de Brasília
    pedido = PedidoBuscaPorCoordenadas(latitude=-15.7942, longitude=-47.8822)
    assert pedido.latitude == -15.7942
    assert pedido.longitude == -47.8822


def test_schema_coordenadas_limites_aceitos():
    """
    Testa se o schema Pydantic aceita coordenadas nos limites.
    """
    # Limites mínimos
    pedido_min = PedidoBuscaPorCoordenadas(latitude=-90, longitude=-180)
    assert pedido_min.latitude == -90
    assert pedido_min.longitude == -180
    
    # Limites máximos
    pedido_max = PedidoBuscaPorCoordenadas(latitude=90, longitude=180)
    assert pedido_max.latitude == 90
    assert pedido_max.longitude == 180


def test_schema_latitude_fora_range_rejeitada():
    """
    Testa se o schema Pydantic rejeita latitudes fora do range.
    """
    # Latitude acima do limite
    with pytest.raises(ValidationError):
        PedidoBuscaPorCoordenadas(latitude=91, longitude=0)
    
    # Latitude abaixo do limite
    with pytest.raises(ValidationError):
        PedidoBuscaPorCoordenadas(latitude=-91, longitude=0)


def test_schema_longitude_fora_range_rejeitada():
    """
    Testa se o schema Pydantic rejeita longitudes fora do range.
    """
    # Longitude acima do limite
    with pytest.raises(ValidationError):
        PedidoBuscaPorCoordenadas(latitude=0, longitude=181)
    
    # Longitude abaixo do limite
    with pytest.raises(ValidationError):
        PedidoBuscaPorCoordenadas(latitude=0, longitude=-181)


def test_schema_coordenadas_ponto_nulo_aceito():
    """
    Testa se o schema Pydantic aceita o ponto nulo (0, 0).
    """
    pedido = PedidoBuscaPorCoordenadas(latitude=0, longitude=0)
    assert pedido.latitude == 0
    assert pedido.longitude == 0
