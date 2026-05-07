"""
Testes de integração para as tarefas do Celery de processamento de fotos.

Testa o fluxo completo de processamento de fotos, incluindo:
- Extração de EXIF
- Validação de GPS
- Upload para o S3
- Atualizações no banco de dados
"""

import pytest
import uuid
import io
import os
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image
from PIL.ExifTags import TAGS

from app.tasks.photo_tasks import (
    _processar_foto_async, 
    _buscar_registro_foto, 
    _buscar_registro_propriedade,
    _buscar_bytes_foto
)
from app.models.photo import Foto, ValidationStatus
from app.models.property import Propriedade
from app.config import settings


def criar_foto_teste_com_exif(
    coords_gps: tuple = None,
    data_captura: datetime = None
) -> bytes:
    """
    Cria uma foto JPEG de teste com dados EXIF.
    
    Args:
        coords_gps: Tupla de (latitude, longitude) ou None
        data_captura: Data e hora da captura ou None
        
    Returns:
        Bytes da foto com dados EXIF
    """
    # Cria uma imagem de teste simples
    img = Image.new('RGB', (100, 100), color='red')
    
    # Prepara dados EXIF
    exif = img.getexif()
    
    if data_captura:
        # 306 é o código para DateTime no EXIF
        exif[306] = data_captura.strftime("%Y:%m:%d %H:%M:%S")
    
    # Nota: Adicionar dados GPS ao EXIF é complexo, então usaremos mock nos testes
    # para a extração em si, ou focaremos na lógica de negócio.
    
    # Salva imagem com EXIF
    buffer_img = io.BytesIO()
    img.save(buffer_img, format='JPEG', exif=exif)
    return buffer_img.getvalue()


@pytest.mark.asyncio
async def test_buscar_registro_foto_sucesso():
    """Testa a busca de registro de foto no banco de dados."""
    # Mock da sessão do banco de dados
    sessao_mock = AsyncMock()
    resultado_mock = Mock()
    foto_mock = Foto(
        id=uuid.uuid4(),
        property_id=uuid.uuid4(),
        validation_status=ValidationStatus.PENDING.value
    )
    resultado_mock.scalar_one_or_none.return_value = foto_mock
    sessao_mock.execute.return_value = resultado_mock
    
    # Testa a busca
    foto_id = str(foto_mock.id)
    resultado = await _buscar_registro_foto(sessao_mock, foto_id)
    
    assert resultado is not None
    assert resultado.id == foto_mock.id
    assert resultado.validation_status == ValidationStatus.PENDING.value


@pytest.mark.asyncio
async def test_buscar_registro_propriedade_sucesso():
    """Testa a busca de registro de propriedade no banco de dados."""
    # Mock da sessão do banco de dados
    sessao_mock = AsyncMock()
    resultado_mock = Mock()
    propriedade_mock = Propriedade(
        id=uuid.uuid4(),
        car_number="GO-5208707-TEST123",
        total_area_ha=100.0,
        car_status="active"
    )
    resultado_mock.scalar_one_or_none.return_value = propriedade_mock
    sessao_mock.execute.return_value = resultado_mock
    
    # Testa a busca
    propriedade_id = str(propriedade_mock.id)
    resultado = await _buscar_registro_propriedade(sessao_mock, propriedade_id)
    
    assert resultado is not None
    assert resultado.id == propriedade_mock.id
    assert resultado.car_number == "GO-5208707-TEST123"


@pytest.mark.asyncio
async def test_buscar_bytes_foto_sucesso(tmp_path):
    """Testa a recuperação de bytes de foto do sistema de arquivos temporário."""
    # Configura um diretório temporário para o teste
    diretorio_teste = tmp_path / "uploads"
    diretorio_teste.mkdir()
    
    foto_id = str(uuid.uuid4())
    caminho_arquivo = diretorio_teste / f"{foto_id}.tmp"
    conteudo_teste = b"bytes_de_foto_de_teste"
    
    with open(caminho_arquivo, "wb") as f:
        f.write(conteudo_teste)
    
    # Mock das configurações para usar o diretório de teste
    with patch('app.tasks.photo_tasks.settings') as settings_mock:
        settings_mock.upload_temp_dir = str(diretorio_teste)
        
        resultado = await _buscar_bytes_foto(foto_id)
        assert resultado == conteudo_teste


@pytest.mark.asyncio
async def test_processar_foto_fluxo_completo():
    """Testa o fluxo completo de processamento de foto com mocks."""
    foto_id = str(uuid.uuid4())
    propriedade_id = uuid.uuid4()
    
    # 1. Mock do Banco de Dados
    foto_mock = Foto(
        id=uuid.UUID(foto_id),
        property_id=propriedade_id,
        validation_status=ValidationStatus.PENDING.value
    )
    
    propriedade_mock = Propriedade(
        id=propriedade_id,
        car_number="TEST123",
        polygon=None # Será mockado no to_shape
    )
    
    # 2. Mock das funções auxiliares
    with patch('app.tasks.photo_tasks._buscar_registro_foto', new_callable=AsyncMock) as mock_buscar_foto, \
         patch('app.tasks.photo_tasks._buscar_registro_propriedade', new_callable=AsyncMock) as mock_buscar_prop, \
         patch('app.tasks.photo_tasks._buscar_bytes_foto', new_callable=AsyncMock) as mock_buscar_bytes, \
         patch('app.tasks.photo_tasks._remover_arquivo_temporario', new_callable=AsyncMock) as mock_remover, \
         patch('app.tasks.photo_tasks.PhotoService') as MockPhotoService, \
         patch('app.tasks.photo_tasks.to_shape') as mock_to_shape, \
         patch('app.tasks.photo_tasks.AsyncSessionLocal') as mock_db_session:
        
        # Configura mocks
        mock_buscar_foto.return_value = foto_mock
        mock_buscar_prop.return_value = propriedade_mock
        mock_buscar_bytes.return_value = b"bytes_da_foto"
        
        mock_sessao = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_sessao
        
        instancia_servico = Mock()
        MockPhotoService.return_value = instancia_servico
        
        # Mock dos dados EXIF
        from app.services.photo_service import ExifData
        dados_exif = ExifData(
            gps_latitude=-15.0,
            gps_longitude=-47.0,
            capture_date=datetime.now(),
            device_make="Fabricante",
            device_model="Modelo"
        )
        instancia_servico.extract_exif.return_value = dados_exif
        instancia_servico.validate_photo_location.return_value = "validated"
        instancia_servico.upload_to_s3.side_effect = ["url_foto", "url_miniatura"]
        instancia_servico.generate_thumbnail.return_value = b"bytes_miniatura"
        
        # Executa o teste
        resultado = await _processar_foto_async(foto_id)
        
        # Verificações
        assert resultado["status"] == "success"
        assert resultado["s3_url"] == "url_foto"
        assert resultado["status_validacao"] == "validated"
        assert foto_mock.validation_status == "validated"
        assert foto_mock.s3_url == "url_foto"
        
        # Verifica se as funções foram chamadas
        mock_buscar_foto.assert_called_once()
        mock_buscar_bytes.assert_called_once_with(foto_id)
        instancia_servico.extract_exif.assert_called_once()
        mock_remover.assert_called_once_with(foto_id)
        mock_sessao.commit.assert_called_once()
