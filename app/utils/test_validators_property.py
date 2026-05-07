"""
Testes baseados em propriedades para funções de validação.

**Valida: Requirements 1.1, 3.2, 3.3**

Este módulo contém testes baseados em propriedades usando Hypothesis para validar
que as funções de validação funcionam corretamente em todos os casos:
- Validação de formato do número CAR
- Validação de ranges de coordenadas geográficas
"""

import pytest
import string
from hypothesis import given, strategies as st, assume, example

from app.utils.validators import (
    validar_numero_car,
    validar_coordenadas,
    validar_latitude,
    validar_longitude
)


# ============================================================================
# PROPERTY 1: VALIDAÇÃO DE FORMATO DO NÚMERO CAR
# **Valida: Requirements 1.1**
# ============================================================================

# Estratégias para gerar números CAR válidos e inválidos

def gerar_car_valido():
    """
    Estratégia para gerar números CAR válidos.
    Formato: UF-MUNICIPIO-IDENTIFICADOR
    - UF: 2 letras maiúsculas
    - MUNICIPIO: 7 dígitos
    - IDENTIFICADOR: 16 a 32 caracteres alfanuméricos maiúsculos
    """
    # Lista de UFs brasileiras válidas
    ufs_brasileiras = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    return st.builds(
        lambda uf, municipio, identificador: f"{uf}-{municipio}-{identificador}",
        uf=st.sampled_from(ufs_brasileiras),
        municipio=st.text(alphabet=string.digits, min_size=7, max_size=7),
        identificador=st.text(
            alphabet=string.ascii_uppercase + string.digits,
            min_size=16,
            max_size=32
        )
    )


@given(numero_car=gerar_car_valido())
def test_property_car_valido_aceito(numero_car):
    """
    **Property 1: Validação de Formato do Número CAR**
    **Valida: Requirements 1.1**
    
    Propriedade: Para qualquer string que corresponda ao padrão
    ESTADO-MUNICIPIO-IDENTIFICADOR onde:
    - ESTADO é 2 letras maiúsculas
    - MUNICIPIO é 7 dígitos
    - IDENTIFICADOR é 16 a 32 caracteres alfanuméricos maiúsculos
    
    A função de validação DEVE retornar True.
    """
    resultado = validar_numero_car(numero_car)
    assert resultado is True, f"Número CAR válido rejeitado: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_lowercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=7, max_size=7),
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=16,
        max_size=32
    )
)
def test_property_car_letras_minusculas_rejeitado(uf, municipio, identificador):
    """
    **Property 1: Validação de Formato do Número CAR - Letras Minúsculas**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com UF em letras minúsculas DEVEM ser rejeitados.
    """
    numero_car = f"{uf}-{municipio}-{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com letras minúsculas aceito: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_uppercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=1, max_size=6),  # Menos de 7 dígitos
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=16,
        max_size=32
    )
)
def test_property_car_municipio_curto_rejeitado(uf, municipio, identificador):
    """
    **Property 1: Validação de Formato do Número CAR - Município Curto**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com código de município com menos de 7 dígitos
    DEVEM ser rejeitados.
    """
    assume(len(municipio) < 7)  # Garante que o município tem menos de 7 dígitos
    numero_car = f"{uf}-{municipio}-{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com município curto aceito: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_uppercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=8, max_size=10),  # Mais de 7 dígitos
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=16,
        max_size=32
    )
)
def test_property_car_municipio_longo_rejeitado(uf, municipio, identificador):
    """
    **Property 1: Validação de Formato do Número CAR - Município Longo**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com código de município com mais de 7 dígitos
    DEVEM ser rejeitados.
    """
    numero_car = f"{uf}-{municipio}-{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com município longo aceito: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_uppercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=7, max_size=7),
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=1,
        max_size=15  # Menos de 16 caracteres
    )
)
def test_property_car_identificador_curto_rejeitado(uf, municipio, identificador):
    """
    **Property 1: Validação de Formato do Número CAR - Identificador Curto**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com identificador com menos de 16 caracteres
    DEVEM ser rejeitados.
    """
    numero_car = f"{uf}-{municipio}-{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com identificador curto aceito: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_uppercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=7, max_size=7),
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=33,
        max_size=50  # Mais de 32 caracteres
    )
)
def test_property_car_identificador_longo_rejeitado(uf, municipio, identificador):
    """
    **Property 1: Validação de Formato do Número CAR - Identificador Longo**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com identificador com mais de 32 caracteres
    DEVEM ser rejeitados.
    """
    numero_car = f"{uf}-{municipio}-{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com identificador longo aceito: {numero_car}"


@given(
    uf=st.text(alphabet=string.ascii_uppercase, min_size=2, max_size=2),
    municipio=st.text(alphabet=string.digits, min_size=7, max_size=7),
    identificador=st.text(
        alphabet=string.ascii_uppercase + string.digits,
        min_size=16,
        max_size=32
    ),
    separador=st.sampled_from(['/', '_', '.', ' ', ''])  # Separadores inválidos
)
def test_property_car_separador_invalido_rejeitado(uf, municipio, identificador, separador):
    """
    **Property 1: Validação de Formato do Número CAR - Separador Inválido**
    **Valida: Requirements 1.1**
    
    Propriedade: Números CAR com separadores diferentes de '-' (hífen)
    DEVEM ser rejeitados.
    """
    numero_car = f"{uf}{separador}{municipio}{separador}{identificador}"
    resultado = validar_numero_car(numero_car)
    assert resultado is False, f"CAR com separador inválido aceito: {numero_car}"


@given(texto=st.text(min_size=0, max_size=100))
def test_property_car_texto_aleatorio_maioria_rejeitado(texto):
    """
    **Property 1: Validação de Formato do Número CAR - Texto Aleatório**
    **Valida: Requirements 1.1**
    
    Propriedade: A maioria dos textos aleatórios DEVE ser rejeitada
    (apenas textos que casualmente correspondem ao padrão são aceitos).
    """
    resultado = validar_numero_car(texto)
    
    # Se foi aceito, deve realmente corresponder ao padrão
    if resultado:
        import re
        padrao = r"^[A-Z]{2}-\d{7}-[A-Z0-9]{16,32}$"
        assert re.match(padrao, texto), f"Texto inválido aceito: {texto}"


# Casos de borda específicos
@example("GO-5208707-ABCD1234EFGH5678")  # Exemplo válido mínimo (16 chars no ID)
@example("SP-1234567-ABCDEFGHIJKLMNOP1234567890ABCDEF")  # Exemplo válido máximo (32 chars no ID)
@given(numero_car=gerar_car_valido())
def test_property_car_casos_borda_validos(numero_car):
    """
    **Property 1: Validação de Formato do Número CAR - Casos de Borda**
    **Valida: Requirements 1.1**
    
    Propriedade: Casos de borda válidos (identificador com 16 ou 32 caracteres)
    DEVEM ser aceitos.
    """
    resultado = validar_numero_car(numero_car)
    assert resultado is True, f"Caso de borda válido rejeitado: {numero_car}"


# ============================================================================
# PROPERTY 2: VALIDAÇÃO DE RANGE DE COORDENADAS
# **Valida: Requirements 3.2, 3.3**
# ============================================================================

@given(
    latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
def test_property_coordenadas_validas_aceitas(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas**
    **Valida: Requirements 3.2, 3.3**
    
    Propriedade: Para qualquer par de valores numéricos onde:
    - Latitude está no range [-90, 90]
    - Longitude está no range [-180, 180]
    
    A função de validação DEVE retornar True.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is True, f"Coordenadas válidas rejeitadas: lat={latitude}, lon={longitude}"


@given(
    latitude=st.floats(min_value=90.001, max_value=1000, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
def test_property_latitude_acima_range_rejeitada(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Latitude Acima do Range**
    **Valida: Requirement 3.2**
    
    Propriedade: Coordenadas com latitude > 90 DEVEM ser rejeitadas.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is False, f"Latitude acima do range aceita: lat={latitude}, lon={longitude}"


@given(
    latitude=st.floats(min_value=-1000, max_value=-90.001, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
def test_property_latitude_abaixo_range_rejeitada(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Latitude Abaixo do Range**
    **Valida: Requirement 3.2**
    
    Propriedade: Coordenadas com latitude < -90 DEVEM ser rejeitadas.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is False, f"Latitude abaixo do range aceita: lat={latitude}, lon={longitude}"


@given(
    latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=180.001, max_value=1000, allow_nan=False, allow_infinity=False)
)
def test_property_longitude_acima_range_rejeitada(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Longitude Acima do Range**
    **Valida: Requirement 3.3**
    
    Propriedade: Coordenadas com longitude > 180 DEVEM ser rejeitadas.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is False, f"Longitude acima do range aceita: lat={latitude}, lon={longitude}"


@given(
    latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=-1000, max_value=-180.001, allow_nan=False, allow_infinity=False)
)
def test_property_longitude_abaixo_range_rejeitada(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Longitude Abaixo do Range**
    **Valida: Requirement 3.3**
    
    Propriedade: Coordenadas com longitude < -180 DEVEM ser rejeitadas.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is False, f"Longitude abaixo do range aceita: lat={latitude}, lon={longitude}"


@given(longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False))
def test_property_coordenadas_limites_latitude(longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Limites de Latitude**
    **Valida: Requirement 3.2**
    
    Propriedade: Os limites exatos de latitude (-90 e 90) DEVEM ser aceitos.
    """
    # Testa limite inferior
    resultado_min = validar_coordenadas(-90, longitude)
    assert resultado_min is True, f"Limite inferior de latitude rejeitado: lat=-90, lon={longitude}"
    
    # Testa limite superior
    resultado_max = validar_coordenadas(90, longitude)
    assert resultado_max is True, f"Limite superior de latitude rejeitado: lat=90, lon={longitude}"


@given(latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False))
def test_property_coordenadas_limites_longitude(latitude):
    """
    **Property 2: Validação de Range de Coordenadas - Limites de Longitude**
    **Valida: Requirement 3.3**
    
    Propriedade: Os limites exatos de longitude (-180 e 180) DEVEM ser aceitos.
    """
    # Testa limite inferior
    resultado_min = validar_coordenadas(latitude, -180)
    assert resultado_min is True, f"Limite inferior de longitude rejeitado: lat={latitude}, lon=-180"
    
    # Testa limite superior
    resultado_max = validar_coordenadas(latitude, 180)
    assert resultado_max is True, f"Limite superior de longitude rejeitado: lat={latitude}, lon=180"


def test_property_coordenadas_nan_rejeitadas():
    """
    **Property 2: Validação de Range de Coordenadas - NaN**
    **Valida: Requirements 3.2, 3.3**
    
    Propriedade: Coordenadas com valores NaN (Not a Number) DEVEM ser rejeitadas.
    """
    import math
    
    # Testa NaN na latitude
    resultado_lat_nan = validar_coordenadas(float('nan'), 0)
    assert resultado_lat_nan is False, "Latitude NaN aceita"
    
    # Testa NaN na longitude
    resultado_lon_nan = validar_coordenadas(0, float('nan'))
    assert resultado_lon_nan is False, "Longitude NaN aceita"
    
    # Testa NaN em ambas
    resultado_ambos_nan = validar_coordenadas(float('nan'), float('nan'))
    assert resultado_ambos_nan is False, "Ambas coordenadas NaN aceitas"


def test_property_coordenadas_infinito_rejeitadas():
    """
    **Property 2: Validação de Range de Coordenadas - Infinito**
    **Valida: Requirements 3.2, 3.3**
    
    Propriedade: Coordenadas com valores infinitos DEVEM ser rejeitadas.
    """
    # Testa infinito positivo na latitude
    resultado_lat_inf_pos = validar_coordenadas(float('inf'), 0)
    assert resultado_lat_inf_pos is False, "Latitude infinito positivo aceita"
    
    # Testa infinito negativo na latitude
    resultado_lat_inf_neg = validar_coordenadas(float('-inf'), 0)
    assert resultado_lat_inf_neg is False, "Latitude infinito negativo aceita"
    
    # Testa infinito positivo na longitude
    resultado_lon_inf_pos = validar_coordenadas(0, float('inf'))
    assert resultado_lon_inf_pos is False, "Longitude infinito positivo aceita"
    
    # Testa infinito negativo na longitude
    resultado_lon_inf_neg = validar_coordenadas(0, float('-inf'))
    assert resultado_lon_inf_neg is False, "Longitude infinito negativo aceita"


# Casos de borda específicos para coordenadas
@example(-15.7942, -47.8822)  # Brasília
@example(0, 0)  # Ponto nulo (Golfo da Guiné)
@example(90, 180)  # Limites máximos
@example(-90, -180)  # Limites mínimos
@example(90, -180)  # Polo Norte, antimeridiano oeste
@example(-90, 180)  # Polo Sul, antimeridiano leste
@given(
    latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
def test_property_coordenadas_casos_borda(latitude, longitude):
    """
    **Property 2: Validação de Range de Coordenadas - Casos de Borda**
    **Valida: Requirements 3.2, 3.3**
    
    Propriedade: Casos de borda conhecidos (polos, antimeridiano, equador, meridiano)
    DEVEM ser aceitos.
    """
    resultado = validar_coordenadas(latitude, longitude)
    assert resultado is True, f"Caso de borda rejeitado: lat={latitude}, lon={longitude}"


# ============================================================================
# TESTES ADICIONAIS PARA FUNÇÕES INDIVIDUAIS
# ============================================================================

@given(latitude=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False))
def test_property_validar_latitude_valida(latitude):
    """
    **Property 2: Validação de Latitude Individual**
    **Valida: Requirement 3.2**
    
    Propriedade: Latitudes no range [-90, 90] DEVEM ser aceitas.
    """
    resultado = validar_latitude(latitude)
    assert resultado is True, f"Latitude válida rejeitada: {latitude}"


@given(latitude=st.one_of(
    st.floats(min_value=-1000, max_value=-90.001, allow_nan=False, allow_infinity=False),
    st.floats(min_value=90.001, max_value=1000, allow_nan=False, allow_infinity=False)
))
def test_property_validar_latitude_invalida(latitude):
    """
    **Property 2: Validação de Latitude Individual - Inválida**
    **Valida: Requirement 3.2**
    
    Propriedade: Latitudes fora do range [-90, 90] DEVEM ser rejeitadas.
    """
    resultado = validar_latitude(latitude)
    assert resultado is False, f"Latitude inválida aceita: {latitude}"


@given(longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False))
def test_property_validar_longitude_valida(longitude):
    """
    **Property 2: Validação de Longitude Individual**
    **Valida: Requirement 3.3**
    
    Propriedade: Longitudes no range [-180, 180] DEVEM ser aceitas.
    """
    resultado = validar_longitude(longitude)
    assert resultado is True, f"Longitude válida rejeitada: {longitude}"


@given(longitude=st.one_of(
    st.floats(min_value=-1000, max_value=-180.001, allow_nan=False, allow_infinity=False),
    st.floats(min_value=180.001, max_value=1000, allow_nan=False, allow_infinity=False)
))
def test_property_validar_longitude_invalida(longitude):
    """
    **Property 2: Validação de Longitude Individual - Inválida**
    **Valida: Requirement 3.3**
    
    Propriedade: Longitudes fora do range [-180, 180] DEVEM ser rejeitadas.
    """
    resultado = validar_longitude(longitude)
    assert resultado is False, f"Longitude inválida aceita: {longitude}"
