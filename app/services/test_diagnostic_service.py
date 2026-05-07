"""
Testes unitários para o ServicoDiagnostico.
Focado na lógica de classificação de risco ambiental.
"""

import pytest
from datetime import date, timedelta
from app.services.diagnostic_service import ServicoDiagnostico
from app.models.diagnostic import RiskLevel

@pytest.fixture
def servico():
    return ServicoDiagnostico()

def test_classificar_risco_apto(servico):
    """Testa classificação APTO (Status ativo, sem PRODES, sem DETER)."""
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=0.0,
        alertas_deter=[]
    )
    assert resultado == RiskLevel.APTO

def test_classificar_risco_bloqueio_direto(servico):
    """Testa classificação BLOQUEIO_DIRETO (Status cancelado ou suspenso)."""
    # Cancelado
    assert servico.classificar_risco(
        status_car="cancelado",
        area_sobreposicao_prodes=0.0,
        alertas_deter=[]
    ) == RiskLevel.BLOQUEIO_DIRETO
    
    # Suspenso
    assert servico.classificar_risco(
        status_car="suspenso",
        area_sobreposicao_prodes=0.0,
        alertas_deter=[]
    ) == RiskLevel.BLOQUEIO_DIRETO

def test_classificar_risco_bloqueio_provavel_prodes(servico):
    """Testa BLOQUEIO_PROVAVEL por área PRODES > 10ha."""
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=15.0,
        alertas_deter=[]
    )
    assert resultado == RiskLevel.BLOQUEIO_PROVAVEL

def test_classificar_risco_bloqueio_provavel_deter_recente(servico):
    """Testa BLOQUEIO_PROVAVEL por alerta DETER recente (< 6 meses)."""
    hoje = date.today()
    alertas = [{"data_alerta": hoje - timedelta(days=30)}]
    
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=0.0,
        alertas_deter=alertas
    )
    assert resultado == RiskLevel.BLOQUEIO_PROVAVEL

def test_classificar_risco_alto_prodes(servico):
    """Testa RISCO_ALTO por área PRODES entre 2 e 10ha."""
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=5.0,
        alertas_deter=[]
    )
    assert resultado == RiskLevel.RISCO_ALTO

def test_classificar_risco_alto_multiplos_deter(servico):
    """Testa RISCO_ALTO por múltiplos alertas DETER (antigos)."""
    hoje = date.today()
    # Alertas antigos (> 12 meses) mas múltiplos
    alertas = [
        {"data_alerta": hoje - timedelta(days=400)},
        {"data_alerta": hoje - timedelta(days=450)}
    ]
    
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=0.0,
        alertas_deter=alertas
    )
    assert resultado == RiskLevel.RISCO_ALTO

def test_classificar_risco_medio_prodes_pequeno(servico):
    """Testa RISCO_MEDIO por área PRODES < 2ha."""
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=1.5,
        alertas_deter=[]
    )
    assert resultado == RiskLevel.RISCO_MEDIO

def test_classificar_risco_medio_deter_antigo(servico):
    """Testa RISCO_MEDIO por alerta DETER antigo (> 12 meses)."""
    hoje = date.today()
    alertas = [{"data_alerta": hoje - timedelta(days=400)}]
    
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=0.0,
        alertas_deter=alertas
    )
    assert resultado == RiskLevel.RISCO_MEDIO

def test_classificar_risco_alto_deter_intermediario(servico):
    """Testa RISCO_ALTO por alerta DETER intermediário (6-12 meses)."""
    hoje = date.today()
    # 9 meses atrás
    alertas = [{"data_alerta": hoje - timedelta(days=270)}]
    
    resultado = servico.classificar_risco(
        status_car="ativo",
        area_sobreposicao_prodes=0.0,
        alertas_deter=alertas
    )
    assert resultado == RiskLevel.RISCO_ALTO
