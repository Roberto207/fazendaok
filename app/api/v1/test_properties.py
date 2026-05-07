"""
Testes de integração para os endpoints de busca de propriedades com mocks de banco de dados.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.database import obter_sessao_db
from app.models.property import Propriedade
from datetime import datetime, timezone
import uuid

# Mock da sessão do banco de dados
async def mock_obter_sessao_db():
    session = AsyncMock()
    # Mock do resultado do execute (vazio por padrão)
    session.execute.return_value = MagicMock(scalar_one_or_none=lambda: None)
    yield session

@pytest.fixture
def override_db():
    app.dependency_overrides[obter_sessao_db] = mock_obter_sessao_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_buscar_por_car_sucesso(override_db):
    """Testa a busca de propriedade por CAR com sucesso (mockando o SICAR e o DB)."""
    
    numero_car = "GO-5208707-8888888888888888888888"
    
    # Mock do ServicoSICAR
    with patch("app.api.v1.properties.ServicoSICAR") as mock_sicar_class:
        mock_instance = mock_sicar_class.return_value
        # Usa AsyncMock para métodos assíncronos
        mock_instance.buscar_propriedade_por_car = AsyncMock(return_value={
            "numero_car": numero_car,
            "area_total_ha": 100.0,
            "status_car": "ativo",
            "geometria_geojson": {
                "type": "Polygon",
                "coordinates": [[[-47.9, -15.8], [-47.8, -15.8], [-47.8, -15.7], [-47.9, -15.7], [-47.9, -15.8]]]
            },
            "dados_adicionais": {"fonte": "mock"}
        })
        
        # Mock do retorno da propriedade salva
        with patch("app.api.v1.properties._converter_para_resposta") as mock_conv:
            mock_conv.return_value = {
                "id": str(uuid.uuid4()),
                "numero_car": numero_car,
                "area_total_ha": 100.0,
                "status_car": "ativo",
                "poligono_geojson": {},
                "data_criacao": datetime.now(timezone.utc).isoformat()
            }
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/v1/propriedades/buscar/car",
                    json={"numero_car": numero_car}
                )
            
            assert response.status_code == 200
            dados = response.json()
            assert dados["numero_car"] == numero_car


@pytest.mark.asyncio
async def test_buscar_por_car_invalido(override_db):
    """Testa a validação do formato do número do CAR."""
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/propriedades/buscar/car",
            json={"numero_car": "CAR-INVALIDO"}
        )
        
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_buscar_por_coordenadas_sucesso(override_db):
    """Testa a busca de propriedade por coordenadas."""
    
    with patch("app.api.v1.properties.ServicoSICAR") as mock_sicar_class:
        mock_instance = mock_sicar_class.return_value
        # Usa AsyncMock para métodos assíncronos
        mock_instance.buscar_propriedades_por_coordenadas = AsyncMock(return_value=[
            {"numero_car": "GO-5208707-1111222233334444555566"}
        ])
        
        mock_instance.buscar_propriedade_por_car = AsyncMock(return_value={
            "numero_car": "GO-5208707-1111222233334444555566",
            "area_total_ha": 200.0,
            "status_car": "ativo",
            "geometria_geojson": {
                "type": "Polygon",
                "coordinates": [[[-47.9, -15.8], [-47.8, -15.8], [-47.8, -15.7], [-47.9, -15.7], [-47.9, -15.8]]]
            }
        })
        
        with patch("app.api.v1.properties._converter_para_resposta") as mock_conv:
            mock_conv.return_value = {
                "id": str(uuid.uuid4()),
                "numero_car": "GO-5208707-1111222233334444555566",
                "area_total_ha": 200.0,
                "status_car": "ativo",
                "poligono_geojson": {},
                "data_criacao": datetime.now(timezone.utc).isoformat()
            }
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/v1/propriedades/buscar/coordenadas",
                    json={"latitude": -15.75, "longitude": -47.85}
                )
            
            assert response.status_code == 200
            dados = response.json()
            assert dados["numero_car"] == "GO-5208707-1111222233334444555566"
