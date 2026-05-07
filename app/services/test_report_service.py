"""
Testes unitários para o serviço de relatórios PDF.
"""

import pytest
import uuid
from datetime import datetime
from app.services.report_service import ServicoRelatorio
from app.models.diagnostic import Diagnostico
from app.models.property import Propriedade

@pytest.mark.asyncio
async def test_gerar_pdf_diagnostico_sucesso():
    """
    Testa se o PDF é gerado corretamente (retorna bytes não vazios).
    """
    servico = ServicoRelatorio()
    
    # Mock de Propriedade
    propriedade = Propriedade(
        id=uuid.uuid4(),
        car_number="BR1234567890",
        total_area_ha=500.0,
        car_status="ATIVO",
        dados_adicionais={
            "owner_name": "Fazenda Teste",
            "municipality": "Cuiabá",
            "state": "MT"
        },
        polygon="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))" # Placeholder para o Geometry
    )
    
    # Mock de Diagnostico
    diagnostico = Diagnostico(
        id=uuid.uuid4(),
        property_id=propriedade.id,
        risk_level="APTO",
        prodes_overlap_area_ha=0.0,
        deter_alert_count=0,
        explanation="Propriedade está em total conformidade socioambiental.",
        created_at=datetime.utcnow()
    )
    
    pdf_content = await servico.gerar_pdf_diagnostico(diagnostico, propriedade)
    
    assert isinstance(pdf_content, (bytes, bytearray))
    assert len(pdf_content) > 0
    # Verifica a assinatura do PDF
    assert pdf_content.startswith(b"%PDF")

@pytest.mark.asyncio
async def test_gerar_pdf_risco_alto():
    """
    Testa a geração de PDF para um caso de risco alto.
    """
    servico = ServicoRelatorio()
    
    propriedade = Propriedade(
        car_number="BR0987654321",
        total_area_ha=1200.0,
        car_status="cancelled",
        polygon="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
    )
    
    diagnostico = Diagnostico(
        risk_level="BLOQUEIO_DIRETO",
        prodes_overlap_area_ha=50.5,
        deter_alert_count=5,
        explanation="Bloqueio imediato devido a desmatamento PRODES significativo."
    )
    
    pdf_content = await servico.gerar_pdf_diagnostico(diagnostico, propriedade)
    
    assert pdf_content.startswith(b"%PDF")
    assert len(pdf_content) > 1000 # Deve ter um tamanho razoável
