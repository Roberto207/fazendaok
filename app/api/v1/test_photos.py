"""
Testes de integração para os endpoints de upload de fotos.
"""

import pytest
import io
import uuid
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.database import obter_sessao_db
from app.models.photo import ValidationStatus

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
async def test_upload_foto_sucesso(override_db):
    """Testa o upload de uma foto com sucesso."""
    
    propriedade_id = str(uuid.uuid4())
    # Cria um arquivo de imagem fictício
    file_content = b"fake image content"
    files = {"arquivos": ("test.jpg", file_content, "image/jpeg")}
    
    # Mock do Celery send_task
    with patch("app.api.v1.photos.celery_app.send_task") as mock_send_task:
        mock_send_task.return_value = MagicMock(id="fake-task-id")
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                f"/api/v1/fotos/upload/{propriedade_id}",
                files=files
            )
            
        assert response.status_code == 200
        dados = response.json()
        assert dados["quantidade_aceita"] == 1
        assert len(dados["ids_tarefas"]) == 1
        assert dados["ids_tarefas"][0] == "fake-task-id"


@pytest.mark.asyncio
async def test_upload_arquivo_invalido(override_db):
    """Testa o upload de um arquivo que não é imagem."""
    
    propriedade_id = str(uuid.uuid4())
    files = {"arquivos": ("test.txt", b"not an image", "text/plain")}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/fotos/upload/{propriedade_id}",
            files=files
        )
        
    assert response.status_code == 200
    dados = response.json()
    assert dados["quantidade_aceita"] == 0
    assert dados["quantidade_rejeitada"] == 1
    assert "apenas imagens são permitidas" in dados["mensagens"][0]
