# Validadores e Testes de Propriedade

## Visão Geral

Este módulo contém funções de validação puras e testes baseados em propriedades (property-based testing) para a Plataforma FazendaOk.

## Arquivos

### `validators.py`
Contém funções de validação puras que podem ser reutilizadas em toda a aplicação:

- **`validar_numero_car(numero_car: str) -> bool`**
  - Valida o formato do número CAR (Cadastro Ambiental Rural)
  - Formato esperado: `UF-MUNICIPIO-IDENTIFICADOR`
  - Exemplo: `GO-5208707-ABCD1234EFGH5678`

- **`validar_coordenadas(latitude: float, longitude: float) -> bool`**
  - Valida se coordenadas geográficas estão dentro dos ranges válidos
  - Latitude: -90 a 90 graus
  - Longitude: -180 a 180 graus

- **`validar_latitude(latitude: float) -> bool`**
  - Valida apenas a latitude

- **`validar_longitude(longitude: float) -> bool`**
  - Valida apenas a longitude

### `test_validators_property.py`
Contém 23 testes baseados em propriedades usando Hypothesis:

#### Property 1: Validação de Formato do Número CAR
**Valida: Requirements 1.1**

Testes que verificam:
- ✅ Números CAR válidos são aceitos
- ✅ Letras minúsculas são rejeitadas
- ✅ Código de município com tamanho incorreto é rejeitado
- ✅ Identificador com tamanho incorreto é rejeitado
- ✅ Separadores inválidos são rejeitados
- ✅ Textos aleatórios são rejeitados (exceto se casualmente válidos)
- ✅ Casos de borda (16 e 32 caracteres no identificador) são aceitos

#### Property 2: Validação de Range de Coordenadas
**Valida: Requirements 3.2, 3.3**

Testes que verificam:
- ✅ Coordenadas válidas são aceitas
- ✅ Latitude fora do range [-90, 90] é rejeitada
- ✅ Longitude fora do range [-180, 180] é rejeitada
- ✅ Limites exatos (-90, 90, -180, 180) são aceitos
- ✅ Valores NaN são rejeitados
- ✅ Valores infinitos são rejeitados
- ✅ Casos de borda conhecidos (polos, antimeridiano) são aceitos
- ✅ Validações individuais de latitude e longitude funcionam corretamente

### `test_validators_integration.py`
Contém 8 testes de integração que verificam:
- ✅ Schemas Pydantic usam corretamente as funções de validação
- ✅ Mensagens de erro são apropriadas
- ✅ Validação funciona em contexto real da aplicação

## Executando os Testes

### Todos os testes de validação
```bash
python3 -m pytest app/utils/ -v
```

### Apenas testes de propriedade
```bash
python3 -m pytest app/utils/test_validators_property.py -v
```

### Apenas testes de integração
```bash
python3 -m pytest app/utils/test_validators_integration.py -v
```

### Com cobertura de código
```bash
python3 -m pytest app/utils/ --cov=app.utils --cov-report=html
```

## Property-Based Testing com Hypothesis

Os testes de propriedade usam o framework [Hypothesis](https://hypothesis.readthedocs.io/) para gerar automaticamente centenas de casos de teste.

### Vantagens

1. **Cobertura Abrangente**: Hypothesis gera automaticamente casos de teste que você não pensaria manualmente
2. **Detecção de Edge Cases**: Encontra casos de borda e situações extremas
3. **Shrinking Automático**: Quando um teste falha, Hypothesis simplifica o caso de teste para o exemplo mínimo que reproduz o erro
4. **Regressão**: Casos de teste que falharam são salvos e re-executados automaticamente

### Estratégias Usadas

#### Para Números CAR
- Geração de UFs brasileiras válidas
- Geração de códigos de município (7 dígitos)
- Geração de identificadores (16-32 caracteres alfanuméricos)
- Variações de case (maiúsculas/minúsculas)
- Separadores inválidos
- Tamanhos incorretos

#### Para Coordenadas
- Floats dentro dos ranges válidos
- Floats fora dos ranges
- Valores nos limites exatos
- Valores especiais (NaN, infinito)
- Combinações de valores válidos e inválidos

## Integração com Pydantic

As funções de validação são usadas nos schemas Pydantic para garantir consistência:

```python
from app.utils.validators import validar_numero_car

class PedidoBuscaPorCAR(BaseModel):
    numero_car: str
    
    @field_validator("numero_car")
    def validar_formato_car(cls, v):
        if not validar_numero_car(v):
            raise ValueError("Formato de CAR inválido")
        return v
```

Isso garante que:
1. A lógica de validação está em um único lugar
2. Os testes de propriedade validam a mesma lógica usada em produção
3. A validação pode ser reutilizada em diferentes contextos

## Exemplos de Uso

### Validação de CAR
```python
from app.utils.validators import validar_numero_car

# Válido
assert validar_numero_car("GO-5208707-ABCD1234EFGH5678") == True

# Inválido - letras minúsculas
assert validar_numero_car("go-5208707-abcd1234efgh5678") == False

# Inválido - sem separadores
assert validar_numero_car("GO5208707ABCD1234EFGH5678") == False
```

### Validação de Coordenadas
```python
from app.utils.validators import validar_coordenadas

# Válido - Brasília
assert validar_coordenadas(-15.7942, -47.8822) == True

# Válido - limites
assert validar_coordenadas(-90, -180) == True
assert validar_coordenadas(90, 180) == True

# Inválido - fora do range
assert validar_coordenadas(91, 0) == False
assert validar_coordenadas(0, 181) == False

# Inválido - valores especiais
assert validar_coordenadas(float('nan'), 0) == False
assert validar_coordenadas(float('inf'), 0) == False
```

## Estatísticas dos Testes

- **Total de testes**: 31
- **Testes de propriedade**: 23
- **Testes de integração**: 8
- **Tempo de execução**: ~1.5 segundos
- **Taxa de sucesso**: 100%

## Requisitos Validados

- **Requirement 1.1**: Validação de formato do número CAR
- **Requirement 3.2**: Validação de range de latitude
- **Requirement 3.3**: Validação de range de longitude

## Manutenção

Ao adicionar novas validações:

1. Crie a função de validação pura em `validators.py`
2. Adicione docstrings com exemplos
3. Crie testes de propriedade em `test_validators_property.py`
4. Adicione testes de integração se necessário
5. Atualize este README

## Referências

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing](https://increment.com/testing/in-praise-of-property-based-testing/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
