"""
Funções de validação puras para a Plataforma FazendaOk.

Este módulo contém funções de validação que podem ser testadas
independentemente e reutilizadas em diferentes partes da aplicação.
"""

import re
from typing import Tuple


def validar_numero_car(numero_car: str) -> bool:
    """
    Valida o formato do número do CAR (Cadastro Ambiental Rural).
    
    O formato esperado é: ESTADO-MUNICIPIO-IDENTIFICADOR
    - ESTADO: 2 letras maiúsculas (UF)
    - MUNICIPIO: 7 dígitos
    - IDENTIFICADOR: 16 a 32 caracteres alfanuméricos maiúsculos
    
    Args:
        numero_car: String contendo o número do CAR a ser validado
        
    Returns:
        True se o formato é válido, False caso contrário
        
    Examples:
        >>> validar_numero_car("GO-5208707-ABCD1234EFGH5678")
        True
        >>> validar_numero_car("go-5208707-abcd1234")  # Letras minúsculas
        False
        >>> validar_numero_car("GO-123-ABC")  # Município com poucos dígitos
        False
        >>> validar_numero_car("GO5208707ABCD1234")  # Sem separadores
        False
    """
    # Padrão: UF (2 letras maiúsculas) - Município (7 dígitos) - Identificador (16-32 alfanuméricos maiúsculos)
    padrao = r"^[A-Z]{2}-\d{7}-[A-Z0-9]{16,32}$"
    
    # Verifica se a string corresponde ao padrão
    return bool(re.match(padrao, numero_car))


def validar_coordenadas(latitude: float, longitude: float) -> bool:
    """
    Valida se as coordenadas geográficas estão dentro dos ranges válidos.
    
    Ranges válidos:
    - Latitude: -90 a 90 graus (Sul a Norte)
    - Longitude: -180 a 180 graus (Oeste a Leste)
    
    Args:
        latitude: Valor da latitude em graus decimais
        longitude: Valor da longitude em graus decimais
        
    Returns:
        True se ambas as coordenadas estão dentro dos ranges válidos, False caso contrário
        
    Examples:
        >>> validar_coordenadas(-15.7942, -47.8822)  # Brasília
        True
        >>> validar_coordenadas(0, 0)  # Ponto nulo (Golfo da Guiné)
        True
        >>> validar_coordenadas(90, 180)  # Limites máximos
        True
        >>> validar_coordenadas(-90, -180)  # Limites mínimos
        True
        >>> validar_coordenadas(91, 0)  # Latitude fora do range
        False
        >>> validar_coordenadas(0, 181)  # Longitude fora do range
        False
        >>> validar_coordenadas(float('nan'), 0)  # NaN
        False
        >>> validar_coordenadas(float('inf'), 0)  # Infinito
        False
    """
    # Verifica se os valores são números válidos (não NaN ou infinito)
    try:
        # Tenta converter para float para garantir que são números
        lat = float(latitude)
        lon = float(longitude)
        
        # Verifica se não são NaN ou infinito
        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
            return False
        
        # Importa math para verificar NaN e infinito
        import math
        if math.isnan(lat) or math.isnan(lon) or math.isinf(lat) or math.isinf(lon):
            return False
        
        # Verifica os ranges
        latitude_valida = -90 <= lat <= 90
        longitude_valida = -180 <= lon <= 180
        
        return latitude_valida and longitude_valida
        
    except (TypeError, ValueError):
        # Se não puder converter para float, é inválido
        return False


def validar_latitude(latitude: float) -> bool:
    """
    Valida se a latitude está dentro do range válido.
    
    Range válido: -90 a 90 graus (Sul a Norte)
    
    Args:
        latitude: Valor da latitude em graus decimais
        
    Returns:
        True se a latitude está dentro do range válido, False caso contrário
        
    Examples:
        >>> validar_latitude(0)
        True
        >>> validar_latitude(90)
        True
        >>> validar_latitude(-90)
        True
        >>> validar_latitude(91)
        False
        >>> validar_latitude(-91)
        False
    """
    try:
        lat = float(latitude)
        import math
        if math.isnan(lat) or math.isinf(lat):
            return False
        return -90 <= lat <= 90
    except (TypeError, ValueError):
        return False


def validar_longitude(longitude: float) -> bool:
    """
    Valida se a longitude está dentro do range válido.
    
    Range válido: -180 a 180 graus (Oeste a Leste)
    
    Args:
        longitude: Valor da longitude em graus decimais
        
    Returns:
        True se a longitude está dentro do range válido, False caso contrário
        
    Examples:
        >>> validar_longitude(0)
        True
        >>> validar_longitude(180)
        True
        >>> validar_longitude(-180)
        True
        >>> validar_longitude(181)
        False
        >>> validar_longitude(-181)
        False
    """
    try:
        lon = float(longitude)
        import math
        if math.isnan(lon) or math.isinf(lon):
            return False
        return -180 <= lon <= 180
    except (TypeError, ValueError):
        return False
