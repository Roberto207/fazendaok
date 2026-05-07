"""
Endpoints de API para upload e gerenciamento de fotos de propriedades.
"""

import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import obter_sessao_db
from app.models.property import Propriedade
from app.models.photo import Foto, ValidationStatus
from app.schemas.photo import RespostaFoto, RespostaUploadFoto
from app.config import settings
from app.celery_app import celery_app

router = APIRouter()


@router.post("/upload/{propriedade_id}", response_model=RespostaUploadFoto)
async def upload_fotos(
    propriedade_id: str,
    arquivos: List[UploadFile] = File(...),
    db: AsyncSession = Depends(obter_sessao_db)
):
    """
    Realiza o upload de um lote de fotos para uma propriedade.
    As fotos são salvas temporariamente e processadas de forma assíncrona.
    """
    # 1. Verifica se a propriedade existe
    resultado = await db.execute(
        select(Propriedade).where(Propriedade.id == uuid.UUID(propriedade_id))
    )
    propriedade = resultado.scalar_one_or_none()
    
    if not propriedade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriedade não encontrada."
        )
    
    # 2. Valida o limite de arquivos
    if len(arquivos) > settings.max_fotos_por_upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite de {settings.max_fotos_por_upload} fotos por upload excedido."
        )
    
    # 3. Processa cada arquivo
    ids_fotos = []
    ids_tarefas = []
    erros = []
    
    # Garante que o diretório temporário existe
    os.makedirs(settings.upload_temp_dir, exist_ok=True)
    
    for arquivo in arquivos:
        # Valida tipo de arquivo (apenas imagens)
        if not arquivo.content_type.startswith("image/"):
            erros.append(f"Arquivo {arquivo.filename} rejeitado: apenas imagens são permitidas.")
            continue
            
        foto_id = uuid.uuid4()
        extensao = os.path.splitext(arquivo.filename)[1]
        caminho_temp = os.path.join(settings.upload_temp_dir, f"{foto_id}{extensao}")
        
        try:
            # Salva o arquivo temporariamente
            async with aiofiles.open(caminho_temp, "wb") as f:
                conteudo = await arquivo.read()
                # Valida tamanho
                if len(conteudo) > settings.max_foto_size_mb * 1024 * 1024:
                    erros.append(f"Arquivo {arquivo.filename} muito grande. Máximo {settings.max_foto_size_mb}MB.")
                    continue
                await f.write(conteudo)
            
            # Cria registro no banco de dados (pendente)
            nova_foto = Foto(
                id=foto_id,
                property_id=propriedade.id,
                validation_status=ValidationStatus.PENDING.value
            )
            db.add(nova_foto)
            ids_fotos.append(str(foto_id))
            
            # Dispara a tarefa Celery para processamento
            tarefa = celery_app.send_task(
                "app.tasks.photo_tasks.processar_tarefa_foto",
                args=[str(foto_id)]
            )
            ids_tarefas.append(tarefa.id)
            
        except Exception as e:
            erros.append(f"Erro ao processar {arquivo.filename}: {str(e)}")
    
    await db.commit()
    
    return RespostaUploadFoto(
        ids_fotos=ids_fotos,
        ids_tarefas=ids_tarefas,
        quantidade_aceita=len(ids_fotos),
        quantidade_rejeitada=len(erros),
        mensagens=erros if erros else None
    )


@router.get("/propriedade/{propriedade_id}", response_model=List[RespostaFoto])
async def listar_fotos_propriedade(
    propriedade_id: str,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """Retorna a lista de fotos associadas a uma propriedade."""
    resultado = await db.execute(
        select(Foto)
        .where(Foto.property_id == uuid.UUID(propriedade_id))
        .order_by(Foto.created_at.desc())
    )
    fotos = resultado.scalars().all()
    
    return fotos
