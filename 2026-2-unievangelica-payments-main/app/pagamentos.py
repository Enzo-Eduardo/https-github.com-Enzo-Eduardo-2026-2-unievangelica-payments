#!/usr/bin/env python3

def calcular_desconto(valor, taxa_desconto):
    """Calcula o valor com desconto."""
    desconto = valor * (taxa_desconto / 100)
    return valor - desconto

def aplicar_juros_atraso(valor, dias_atraso):
    """Aplica juros simples de 1% ao dia."""
    juros = valor * (0.01 * dias_atraso)
    return valor + juros

def validar_metodo_pagamento(metodo):
    """Valida se o método de pagamento é aceito."""
    metodos_aceitos = ["pix", "cartao_credito", "cartao_debito", "boleto"]
    return metodo.lower() in metodos_aceitos

def processar_reembolso(valor_pago, valor_reembolso):
    """Verifica se o reembolso é válido e retorna o saldo restante.
    Retorna -1 caso o reembolso solicitado seja maior que o pago."""
    if valor_reembolso > valor_pago:
        return -1 
    return valor_pago - valor_reembolso

if __name__ == "__main__":
    print("=== Sistema de Teste Interativo de Pagamentos ===")
    while True:
        print("\nOpções de Teste Manual:")
        print("1 - Calcular Desconto")
        print("2 - Aplicar Juros de Atraso")
        print("3 - Validar Método de Pagamento")
        print("4 - Processar Reembolso")
        print("0 - Sair")
        
        opcao = input("Escolha a função que deseja testar: ")
        
        if opcao == "1":
            v = float(input("Digite o valor (R$): "))
            t = float(input("Digite a taxa de desconto (%): "))
            print(f">>> Valor com desconto: R$ {calcular_desconto(v, t):.2f}")
            
        elif opcao == "2":
            v = float(input("Digite o valor (R$): "))
            d = int(input("Digite os dias de atraso: "))
            print(f">>> Valor com juros: R$ {aplicar_juros_atraso(v, d):.2f}")
            
        elif opcao == "3":
            metodo = input("Digite o método de pagamento (ex: pix, boleto, cheque): ")
            valido = validar_metodo_pagamento(metodo)
            print(f">>> O método '{metodo}' é válido? {'Sim' if valido else 'Não'}")
            
        elif opcao == "4":
            vp = float(input("Digite o valor pago (R$): "))
            vr = float(input("Digite o valor do reembolso (R$): "))
            resultado = processar_reembolso(vp, vr)
            if resultado == -1:
                print(">>> Reembolso inválido: valor solicitado maior que o pago.")
            else:
                print(f">>> Saldo restante: R$ {resultado:.2f}")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida!")