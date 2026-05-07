"""
Tarefas do Celery para processamento de fotos na Plataforma FazendaOk.

Este módulo implementa o processamento assíncrono de fotos, incluindo:
- Extração de dados EXIF
- Validação de coordenadas GPS em relação aos limites da propriedade
- Upload da foto para o S3
- Geração e upload de miniatura (thumbnail) para o S3
- Atualização dos registros no banco de dados
"""

import logging
import os
import asyncio
from uuid import UUID
from typing import Optional
from celery import Task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.photo import Foto, ValidationStatus
from app.models.property import Propriedade
from app.services.photo_service import PhotoService
from app.config import settings

# Configuração do logger
logger = logging.getLogger(__name__)


class TarefaProcessamentoFoto(Task):
    """Classe base para tarefas de processamento de foto com configuração de rebatida (retry)."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutos
    retry_jitter = True


@celery_app.task(
    bind=True,
    base=TarefaProcessamentoFoto,
    name="app.tasks.photo_tasks.processar_tarefa_foto"
)
def processar_tarefa_foto(self, foto_id: str) -> dict:
    """
    Processa uma foto enviada de forma assíncrona.
    
    Esta tarefa:
    1. Busca o registro da foto no banco de dados
    2. Extrai dados EXIF (coordenadas GPS, data de captura, info do dispositivo)
    3. Valida as coordenadas GPS contra o polígono da propriedade
    4. Faz o upload da foto para o S3
    5. Gera e faz o upload da miniatura para o S3
    6. Atualiza o registro da foto com as URLs do S3 e o status de validação
    
    Args:
        foto_id: UUID do registro da foto a ser processada
        
    Returns:
        dict: Resultado do processamento com status e detalhes
        
    Raises:
        Exception: Se o processamento falhar após todas as tentativas
    """
    logger.info(f"Iniciando processamento da foto foto_id={foto_id}")
    
    try:
        # Executa o processamento assíncrono no loop de eventos
        resultado = asyncio.run(_processar_foto_async(foto_id))
        logger.info(f"Processamento da foto concluído para foto_id={foto_id}: {resultado}")
        return resultado
        
    except Exception as e:
        logger.error(f"Falha no processamento da foto foto_id={foto_id}: {str(e)}", exc_info=True)
        raise


async def _processar_foto_async(foto_id: str) -> dict:
    """
    Implementação assíncrona do processamento de foto.
    
    Args:
        foto_id: UUID do registro da foto a ser processada
        
    Returns:
        dict: Resultado do processamento com status e detalhes
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. Busca o registro da foto no banco de dados
            foto = await _buscar_registro_foto(session, foto_id)
            if not foto:
                raise ValueError(f"Registro de foto não encontrado: {foto_id}")
            
            logger.info(f"Registro de foto recuperado: {foto.id}, property_id={foto.property_id}")
            
            # 2. Busca o registro da propriedade para obter o polígono
            propriedade = await _buscar_registro_propriedade(session, str(foto.property_id))
            if not propriedade:
                raise ValueError(f"Registro de propriedade não encontrado: {foto.property_id}")
            
            logger.info(f"Registro de propriedade recuperado: {propriedade.id}, car_number={propriedade.car_number}")
            
            # Inicializa o serviço de fotos
            servico_foto = PhotoService(
                aws_access_key_id=settings.aws_access_key_id or "",
                aws_secret_access_key=settings.aws_secret_access_key or "",
                aws_bucket_name=settings.aws_bucket_name,
                aws_endpoint_url=settings.aws_endpoint_url
            )
            
            # 3. Busca os bytes da foto do armazenamento temporário
            bytes_foto = await _buscar_bytes_foto(foto_id)
            
            # 4. Extrai dados EXIF
            dados_exif = servico_foto.extract_exif(bytes_foto)
            logger.info(f"Dados EXIF extraídos: GPS=({dados_exif.gps_latitude}, {dados_exif.gps_longitude}), "
                       f"data_captura={dados_exif.capture_date}")
            
            # 5. Valida coordenadas GPS contra o polígono da propriedade
            status_validacao = ValidationStatus.NO_GPS_SESSION_VALID.value
            
            if dados_exif.gps_latitude is not None and dados_exif.gps_longitude is not None:
                # Converte polígono da propriedade de PostGIS para Shapely
                poligono_propriedade = to_shape(propriedade.polygon)
                
                # Valida localização da foto
                resultado_validacao = servico_foto.validate_photo_location(
                    gps_coords=(dados_exif.gps_latitude, dados_exif.gps_longitude),
                    property_polygon=poligono_propriedade
                )
                status_validacao = resultado_validacao
                logger.info(f"Resultado da validação da foto: {status_validacao}")
            else:
                logger.warning(f"Nenhuma coordenada GPS encontrada nos dados EXIF, marcando como no_gps_session_valid")
            
            # 6. Upload da foto para o S3
            chave_foto = f"photos/{foto.property_id}/{foto.id}.jpg"
            url_s3 = servico_foto.upload_to_s3(bytes_foto, chave_foto)
            logger.info(f"Foto enviada para o S3: {url_s3}")
            
            # 7. Gera e envia miniatura
            bytes_miniatura = servico_foto.generate_thumbnail(bytes_foto)
            chave_miniatura = f"photos/{foto.property_id}/thumbnails/{foto.id}_thumb.jpg"
            url_s3_miniatura = servico_foto.upload_to_s3(bytes_miniatura, chave_miniatura)
            logger.info(f"Miniatura enviada para o S3: {url_s3_miniatura}")
            
            # 8. Atualiza o registro da foto com os resultados
            foto.s3_url = url_s3
            foto.thumbnail_s3_url = url_s3_miniatura
            foto.gps_latitude = dados_exif.gps_latitude
            foto.gps_longitude = dados_exif.gps_longitude
            foto.validation_status = status_validacao
            foto.capture_date = dados_exif.capture_date
            foto.exif_metadata = {
                "device_make": dados_exif.device_make,
                "device_model": dados_exif.device_model,
                "raw_exif": dados_exif.raw_exif
            }
            
            # Atualiza geometria do ponto GPS se as coordenadas existirem
            if dados_exif.gps_latitude is not None and dados_exif.gps_longitude is not None:
                from geoalchemy2.elements import WKTElement
                foto.gps_point = WKTElement(
                    f"POINT({dados_exif.gps_longitude} {dados_exif.gps_latitude})",
                    srid=4326
                )
            
            await session.commit()
            logger.info(f"Registro de foto atualizado no banco de dados: {foto.id}")
            
            # 9. Remove o arquivo temporário
            await _remover_arquivo_temporario(foto_id)
            
            return {
                "status": "success",
                "foto_id": str(foto.id),
                "s3_url": url_s3,
                "thumbnail_s3_url": url_s3_miniatura,
                "status_validacao": status_validacao,
                "coordenadas_gps": {
                    "latitude": dados_exif.gps_latitude,
                    "longitude": dados_exif.gps_longitude
                } if dados_exif.gps_latitude and dados_exif.gps_longitude else None,
                "data_captura": dados_exif.capture_date.isoformat() if dados_exif.capture_date else None
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Erro ao processar foto {foto_id}: {str(e)}", exc_info=True)
            
            # Atualiza status da foto para falha
            try:
                foto = await _buscar_registro_foto(session, foto_id)
                if foto:
                    foto.validation_status = ValidationStatus.FAILED.value
                    await session.commit()
            except Exception as erro_atualizacao:
                logger.error(f"Falha ao atualizar status da foto para falha: {str(erro_atualizacao)}")
            
            raise


async def _buscar_registro_foto(session: AsyncSession, foto_id: str) -> Optional[Foto]:
    """
    Busca o registro da foto no banco de dados.
    
    Args:
        session: Sessão do banco de dados
        foto_id: UUID da foto
        
    Returns:
        Objeto Foto ou None se não encontrado
    """
    try:
        foto_uuid = UUID(foto_id)
        resultado = await session.execute(
            select(Foto).where(Foto.id == foto_uuid)
        )
        return resultado.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Erro ao buscar registro da foto: {str(e)}")
        raise


async def _buscar_registro_propriedade(session: AsyncSession, propriedade_id: str) -> Optional[Propriedade]:
    """
    Busca o registro da propriedade no banco de dados.
    
    Args:
        session: Sessão do banco de dados
        propriedade_id: UUID da propriedade
        
    Returns:
        Objeto Propriedade ou None se não encontrado
    """
    try:
        propriedade_uuid = UUID(propriedade_id)
        resultado = await session.execute(
            select(Propriedade).where(Propriedade.id == propriedade_uuid)
        )
        return resultado.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Erro ao buscar registro da propriedade: {str(e)}")
        raise


async def _buscar_bytes_foto(foto_id: str) -> bytes:
    """
    Busca os bytes da foto no armazenamento temporário local.
    
    Args:
        foto_id: ID da foto
        
    Returns:
        Bytes da foto
        
    Raises:
        FileNotFoundError: Se o arquivo temporário não for encontrado
    """
    caminho_arquivo = os.path.join(settings.upload_temp_dir, f"{foto_id}.tmp")
    
    if not os.path.exists(caminho_arquivo):
        logger.error(f"Arquivo temporário não encontrado: {caminho_arquivo}")
        raise FileNotFoundError(f"Arquivo temporário da foto {foto_id} não encontrado.")
    
    # Executa a leitura do arquivo em um thread pool para não bloquear o loop de eventos
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _ler_arquivo, caminho_arquivo)


def _ler_arquivo(caminho: str) -> bytes:
    """Lê um arquivo de forma síncrona."""
    with open(caminho, "rb") as f:
        return f.read()


async def _remover_arquivo_temporario(foto_id: str):
    """
    Remove o arquivo temporário após o processamento.
    
    Args:
        foto_id: ID da foto
    """
    caminho_arquivo = os.path.join(settings.upload_temp_dir, f"{foto_id}.tmp")
    if os.path.exists(caminho_arquivo):
        try:
            os.remove(caminho_arquivo)
            logger.info(f"Arquivo temporário removido: {caminho_arquivo}")
        except Exception as e:
            logger.warning(f"Falha ao remover arquivo temporário {caminho_arquivo}: {str(e)}")
