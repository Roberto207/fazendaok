"""
Testes de integração para o endpoint de dashboard.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.database import obter_sessao_db

# Mock da sessão do banco de dados
async def mock_obter_sessao_db():
    session = AsyncMock()
    
    # Mock do resultado da estatística de propriedades
    mock_prop = MagicMock()
    mock_prop.total = 10
    mock_prop.area = 500.5
    
    # Mock do resultado da estatística de fotos
    mock_foto = MagicMock()
    mock_foto.total = 50
    mock_foto.validadas = 40
    mock_foto.invalidas = 5
    mock_foto.pendentes = 5
    
    # Simula o retorno de múltiplos executes
    session.execute.side_effect = [
        MagicMock(first=lambda: mock_prop),
        MagicMock(first=lambda: mock_foto),
        MagicMock(scalars=lambda: MagicMock(all=lambda: []))
    ]
    
    yield session

@pytest.fixture
def override_db():
    app.dependency_overrides[obter_sessao_db] = mock_obter_sessao_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_obter_resumo_dashboard_sucesso(override_db):
    """Testa a recuperação do resumo do dashboard."""
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/resumo")
        
    assert response.status_code == 200
    dados = response.json()
    assert dados["propriedades"]["total_propriedades"] == 10
    assert dados["propriedades"]["total_area_ha"] == 500.5
    assert dados["fotos"]["total_fotos"] == 50
    assert dados["fotos"]["fotos_validadas"] == 40
