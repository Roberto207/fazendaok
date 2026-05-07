"""
Testes de integração para os endpoints de diagnóstico.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.database import obter_sessao_db
from datetime import datetime, timezone

# Mock da sessão do banco de dados
async def mock_obter_sessao_db():
    session = AsyncMock()
    # Mock do resultado da busca por propriedade (sucesso)
    session.execute.return_value = MagicMock(scalar_one_or_none=lambda: MagicMock(id=uuid.uuid4()))
    yield session

@pytest.fixture
def override_db():
    app.dependency_overrides[obter_sessao_db] = mock_obter_sessao_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_gerar_diagnostico_sucesso(override_db):
    """Testa a solicitação de geração de diagnóstico."""
    
    propriedade_id = str(uuid.uuid4())
    
    # Mock do Celery send_task
    with patch("app.api.v1.diagnostics.celery_app.send_task") as mock_send_task:
        mock_send_task.return_value = MagicMock(id="fake-task-id")
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(f"/api/v1/diagnosticos/gerar/{propriedade_id}")
            
        assert response.status_code == 202
        dados = response.json()
        assert dados["tarefa_id"] == "fake-task-id"
        assert dados["status"] == "PENDING"


@pytest.mark.asyncio
async def test_consultar_status_sucesso():
    """Testa a consulta de status de uma tarefa de diagnóstico."""
    
    tarefa_id = "fake-task-id"
    
    # Mock do AsyncResult do Celery
    with patch("app.api.v1.diagnostics.celery_app.AsyncResult") as mock_result:
        mock_instance = mock_result.return_value
        mock_instance.status = "SUCCESS"
        mock_instance.result = "fake-diag-id"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/diagnosticos/status/{tarefa_id}")
            
        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "SUCCESS"
        assert dados["resultado_id"] == "fake-diag-id"


@pytest.mark.asyncio
async def test_obter_diagnostico_sucesso(override_db):
    """Testa a recuperação de um diagnóstico específico."""
    
    diagnostico_id = str(uuid.uuid4())
    propriedade_id = str(uuid.uuid4())
    
    # Mock da busca no banco
    with patch("app.api.v1.diagnostics.obter_sessao_db") as mock_db_dep:
        session = AsyncMock()
        mock_diag = MagicMock()
        mock_diag.id = diagnostico_id
        mock_diag.propriedade_id = propriedade_id
        mock_diag.nivel_risco = "baixo"
        mock_diag.explicacao_ia = "Tudo certo."
        mock_diag.interseccoes = []
        mock_diag.data_geracao = datetime.now(timezone.utc).isoformat()
        mock_diag.validado = True
        
        session.execute.return_value = MagicMock(scalar_one_or_none=lambda: mock_diag)
        
        # Override local para este teste
        app.dependency_overrides[obter_sessao_db] = lambda: session
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/diagnosticos/{diagnostico_id}")
            
        assert response.status_code == 200
        dados = response.json()
        assert dados["id"] == diagnostico_id
        
        app.dependency_overrides.clear()
