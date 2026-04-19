import pytest
from app.pagamentos import (
    calcular_desconto,
    aplicar_juros_atraso,
    validar_metodo_pagamento,
    processar_reembolso
)

def test_calcular_desconto():
    # Arrange
    valor = 100
    percentual = 10
    
    # Act
    resultado = calcular_desconto(valor, percentual)
    
    # Assert
    assert resultado == 90


def test_aplicar_juros_atraso():
    # Arrange
    valor_pago = 100
    dias_atraso = 5
    dias_ok = 0

    # Act
    resultado_com_atraso = aplicar_juros_atraso(valor_pago, dias_atraso)
    resultado_sem_atraso = aplicar_juros_atraso(valor_pago, dias_ok)

    # Assert
    assert resultado_com_atraso == 105.0
    assert resultado_sem_atraso == 100.0


def test_validar_metodo_pagamento():
    # Arrange
    metodo_valido_pix = "pix"
    metodo_valido_cartao = "cartao_credito"
    metodo_invalido = "cheque"
    
    # Act
    resultado_pix = validar_metodo_pagamento(metodo_valido_pix)
    resultado_cartao = validar_metodo_pagamento(metodo_valido_cartao)
    resultado_invalido = validar_metodo_pagamento(metodo_invalido)
    
    # Assert
    assert resultado_pix is True
    assert resultado_cartao is True
    assert resultado_invalido is False


def test_processar_reembolso():
    # Arrange
    valor_pago = 200
    
    # Act
    reembolso_exato = processar_reembolso(valor_pago, 200)   # Caso de Valor Limite
    reembolso_maior = processar_reembolso(valor_pago, 201)   # Caso de Valor Limite
    reembolso_parcial = processar_reembolso(valor_pago, 50)
    
    # Assert
    assert reembolso_exato == 0
    assert reembolso_maior == -1
    assert reembolso_parcial == 150