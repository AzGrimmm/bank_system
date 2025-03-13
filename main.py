menu = """
[d] - Deposito
[s] - Saque
[e] - Extrato
[q] - Sair
"""

saldo = 0
extrato = ""
soma_saques_diarios = 0
num_de_saq_diarios = 0
transacoes = []
depositos = []
saques = []

LIM_VAL_POR_SAQUE = float(500)
LIM_N_SAQ_DIA = 3
LIM_VAL_SAQ_DIA = float(1500)


while True:
    print(menu)
    opt = input("=> Opção: ")
    match opt:
        case "d":
            while True:
                try:
                    valor_deposito = float(input("Valor: R$"))
                except ValueError:
                    print("ERRO! valor invalido")
                    continue
                if valor_deposito <= 0:
                    print("ERRO! valor deve ser um valor positivo maior que 0!")
                    continue
                saldo += valor_deposito
                depositos.append(valor_deposito)
                print(f"saldo atual = R${saldo:.2f}")
                break
        case "s":
            while True:
                sem_saldo = saldo <= 0

                exc_num_saques_diarios = num_de_saq_diarios >= LIM_N_SAQ_DIA

                exc_valor_saque_diario = soma_saques_diarios >= LIM_VAL_SAQ_DIA

                if sem_saldo:
                    saldo = 0
                    print("Operação falhou! => Não existe nenhum saldo!")
                    break
                elif exc_num_saques_diarios:
                    print(f"Operação falhou! => Limite de {LIM_N_SAQ_DIA} saques diários alcaçados!")
                    break
                elif exc_valor_saque_diario:
                    print(f"Operação falhou! => valor de R${LIM_VAL_SAQ_DIA:.2f} diário atingido!")
                    break
                else:
                    while True:
                        try:
                            valor_saque = float(input("Valor(até R$500): R$"))

                            exc_valor_por_saque = valor_saque > LIM_VAL_POR_SAQUE

                            exc_valor_saque_dia = valor_saque + soma_saques_diarios >= LIM_VAL_SAQ_DIA
                        except ValueError:
                            print("ERRO! valor invalido")
                            continue
                        if exc_valor_por_saque:
                            print("Operação falhou! saque limitado até 500")
                            continue
                        elif exc_valor_saque_dia:
                            print(f"Operação falhou! => o valor excede o limite de R${LIM_VAL_SAQ_DIA}")
                            continue
                        elif valor_saque < 0:
                            print("ERRO! O valor informado é inválido!")
                            continue
                        elif saldo < valor_saque:
                            print("Saldo insuficiente!")
                            continue
                        else:
                            saldo -= valor_saque
                            num_de_saq_diarios += 1
                            saques.append(valor_saque)
                            print(f"saldo atual = R${saldo:.2f}")
                            break
                    break
        case "e":
            texto = "Extrato"
            largura = 40
            print(texto.center(largura).replace(" ", "="))
            print(f"\tsaldo atual = R${saldo:.2f}")
            for _ in saques:
                print(f"\tsaque: {_:.2f}")
            for _ in depositos:
                print(f"\tdeposito: {_:.2f}")
            print("=" * largura)
        case "q":
            print("Fechando sistema...")
            break
        case _:
            print("ERRO! Escolha uma opção válida!")
