from datetime import datetime
import re
from tabulate import tabulate

cpfs_cadastrados = set()
clientes = []
contas_corrente = []


def capsula_ambiente(nome):
    def decorador(func):
        def envelope(*args, **kwargs):
            largura = 40
            print(f"{nome.center(largura).replace('  ', '==')}")
            resultado = func(*args, **kwargs)
            print("=" * largura)
            return resultado  # Retorna o resultado
        return envelope
    return decorador


def pedir_dado(mensagem):
    dado = input(mensagem).strip()
    if dado.lower() == "s":  # Permite "S" ou "s"
        print("Saindo...")
        return None  # Indica que o usuário quer sair
    return dado


def transacoes(cliente, conta):
    @capsula_ambiente("Menu Transações")
    def menu_transacoes():
        menu = """
    \n\t[d] - Deposito
    \t[s] - Saque
    \t[e] - Extrato
    \t[q] - voltar
    """
        print(menu)

    """
    Funções para gerenciar transações bancárias de um cliente.
    """

    @capsula_ambiente("Extrato")
    def extrato(saldo, transacoes):
        """Exibe o saldo atual e as transações realizadas."""
        print(f"\tsaldo atual = R${saldo:.2f}")
        for transacao in transacoes:
            for key, value in transacao.items():
                print(f"\ttransação: {key}: R${value:.2f}")

    def deposito():
        """Solicita um valor de depósito ao usuário, garantindo entrada válida."""
        while True:
            try:
                valor = float(input("Valor: R$"))
                if valor == -1:
                    return False
                if valor <= 0:
                    raise ValueError("O valor deve ser positivo e maior que 0.")
                return valor
            except ValueError as e:
                print(f"ERRO! {e}")

    def saque(saldo, num_saques, soma_saques_diarios):
        """Gerencia a operação de saque, respeitando os limites diários e individuais."""
        LIMITE_SAQUES = 3
        LIMITE_POR_SAQUE = 500.0
        LIMITE_SAQUE_DIA = 1500.0

        if saldo <= 0:
            print("Operação falhou! => Sem saldo.")
            return False
        if num_saques >= LIMITE_SAQUES:
            print(f"Operação falhou! => Limite de {LIMITE_SAQUES} saques diários alcançado!")
            return False

        while True:
            try:
                valor = float(input("Valor (até R$500): R$"))
                if valor == -1:
                    return False
                if valor <= 0:
                    raise ValueError("O valor informado deve ser positivo.")
                if valor > LIMITE_POR_SAQUE:
                    raise ValueError("Saque limitado a R$500 por operação.")
                if valor + soma_saques_diarios > LIMITE_SAQUE_DIA:
                    raise ValueError(f"O valor excede o limite diário de R${LIMITE_SAQUE_DIA}.")
                if saldo < valor:
                    raise ValueError("Saldo insuficiente.")
                return valor
            except ValueError as e:
                print(f"ERRO! {e}")

    while True:
        conta["i"]["saldo"]
        menu_transacoes()
        opt = input("=> Opção: ")
        if opt == "d":
            valor = deposito()
            if valor is False:
                print("Saindo da operação")
                continue
            conta["i"]["saldo"] += valor
            conta["i"]["transacoes"].append({"deposito": valor})
            atualizar_conta_corrente(cliente, conta)
            print(f"saldo atual = R${conta['i']['saldo']:.2f}")
        elif opt == "s":
            valor = saque(conta["i"]["saldo"], conta["i"]["num_saques"], conta["i"]["soma_saques_diarios"])
            if valor is False:
                continue
            conta["i"]["saldo"] -= valor
            conta["i"]["num_saques"] += 1
            conta["i"]["transacoes"].append({"saque": valor})
            conta["i"]["soma_saques_diarios"] += valor
            atualizar_conta_corrente(cliente, conta)
        elif opt == "e":
            extrato(conta["i"]["saldo"], transacoes=conta["i"]["transacoes"])
        elif opt == "q":
            print("Fechando sistema de transações...")
            break
        else:
            print("ERRO! Escolha uma opção válida!")


def buscar_conta_corrente(cliente, contas_corrente):
    if len(cliente["contas"]) == 0:
        return None
    else:
        for i, c in enumerate(cliente["contas"]):
            print(f"[{i}] - Número da conta: {c['nro']}, Agência: {c['agencia']}")

        while True:
            try:
                conta_escolhida = int(input("Qual conta quer acessar?: "))
                if 0 <= conta_escolhida < len(cliente["contas"]):
                    nro_conta = cliente["contas"][conta_escolhida]["nro"]
                    for conta in contas_corrente:
                        if conta["nro"] == nro_conta:
                            return conta
                    print("Conta não encontrada!")
                else:
                    print("Índice inválido. Tente novamente.")
            except ValueError:
                print("Entrada inválida! Digite um número válido.")


def atualizar_conta_corrente(cliente, conta):
    for c in contas_corrente:
        if cliente["cpf"] == c["cpf"]:
            c["i"] = conta["i"]
    print("sucesso")


def area_usuario():
    @capsula_ambiente("Menu Usuário")
    def menu_usuario():
        menu_cliente = """
\t[a] - acessar usuário
\t[c] - cadastrar usuário
\t[l] - listar usuários
\t[q] - fechar sistema
"""
        print(menu_cliente)

    @capsula_ambiente("conta_usúario")
    def menu_conta_usuario():
        menu = """
\t[a] - acessar conta corrente
\t[c] - cadastrar conta correte
\t[q] - sair
"""
        print(menu)

    def validar_nome_completo(nome_completo):
        nome_completo = nome_completo.strip()
        if len(nome_completo.split()) < 2:
            return False
        if not all(palavra.isalpha() and palavra[0].isupper() for palavra in nome_completo.split()):
            return False
        if re.search(r'[^a-zA-ZÀ-ÖØ-öø-ÿ ]', nome_completo):
            return False
        return True

    def validar_cpf(cpf):
        cpf = "".join(filter(str.isdigit, cpf))
        if len(cpf) != 11 or cpf == cpf[0] * 11 or not cpf.isdigit():
            return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        primeiro_digito = (soma * 10 % 11) % 10
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        segundo_digito = (soma * 10 % 11) % 10
        return cpf[-2:] == f"{primeiro_digito}{segundo_digito}"

    def validar_endereco(endereco):
        padrao = r"^([\w\s\.]+) - (\d+\w?) - ([\w\s]+) - ([\w\s]+)\/([A-Z]{2})$"

        match = re.match(padrao, endereco)

        if match:
            logradouro, nro, bairro, cidade, sigla_estado = match.groups()

            # Verificações adicionais
            if len(sigla_estado) != 2:  # UF deve ter 2 letras
                print("Sigla inválida")
                return False

            return True
        return False

    @capsula_ambiente("Cadastro de usuário")
    def cadastro_usuario():
        cliente = {}

        while True:
            while True:
                cpf = pedir_dado("CPF - 's' para sair: ")
                if cpf is None:
                    return False
                if not validar_cpf(cpf):
                    print("CPF inválido! Tente novamente!")
                    continue

                elif cpf in cpfs_cadastrados:  # Só verifica se o CPF já existe depois de validar
                    print("CPF já cadastrado! Tente novamente!")
                    continue
                else:
                    cliente["cpf"] = cpf  # Agora só chega aqui se o CPF for válido e ainda não existir
                    break  # Sai do loop após um CPF válido ser cadastrado
            while True:
                nome = pedir_dado("Nome Completo - 's' para sair: ")
                if nome is None:
                    return False
                if not validar_nome_completo(nome):
                    print("Nome Completo inválido")
                    continue
                cliente["nome"] = nome
                break
            while True:
                dia_nasc = pedir_dado("Dia do nascimento - 's' para sair: ")
                if dia_nasc is None:
                    return False
                mes_nasc = pedir_dado("Mês do nascimento - 's' para sair: ")
                if mes_nasc is None:
                    return False
                ano_nasc = pedir_dado("Ano do nascimento - 's' para sair: ")
                if ano_nasc is None:
                    return False
                data_nasc_str = (dia_nasc + "/" + mes_nasc + "/" + ano_nasc)
                try:
                    data_nasc = datetime.strptime(data_nasc_str, "%d/%m/%Y")
                except (ValueError):
                    print("ERRO! data inválida! insira uma data válida!")
                    continue
                else:
                    data_nasc_str = datetime.strftime(data_nasc, "%d/%m/%Y")
                    cliente["nascimento"] = data_nasc_str
                    break
            while True:
                print("==Endereço==")
                logradouro = pedir_dado("Logradouro - 's' para sair: ")
                if logradouro is None:
                    return False
                nro = pedir_dado("nro - 's' para sair: ")
                if nro is None:
                    return False
                bairro = pedir_dado("bairro - 's' para sair: ")
                if bairro is None:
                    return False
                cidade = pedir_dado("cidade - 's' para sair: ")
                if cidade is None:
                    return False
                sigla_estado = pedir_dado("estado(sigla) - 's' para sair: ")
                if sigla_estado is None:
                    return False
                endereco = f"{logradouro} - {nro} - {bairro} - {cidade}/{sigla_estado}"
                validacao = validar_endereco(endereco)
                if validacao:
                    cliente["endereco"] = endereco
                    break
                else:
                    print("Endereço inválido!")
                    continue
            cliente["contas"] = []
            break
        return cliente if cliente else {}

    def cadastrar_conta_corrente(cpf):
        agencia = "0001"
        nro_conta = len(contas_corrente) + 1 if len(contas_corrente) > 0 else 1
        nova_conta = {"agencia": agencia, "nro": nro_conta, "cpf": cpf, "i": {"saldo": 0, "transacoes": [], "soma_saques_diarios": 0, "num_saques": 0}}
        return nova_conta

    @capsula_ambiente("Acesso ao usuário")
    def acessar_usuario():
        while True:
            cpf = pedir_dado("CPF - 's' para sair: ")
            if cpf is None:
                break
            if validar_cpf(cpf):
                if cpf in cpfs_cadastrados:
                    for cliente in clientes:
                        if cliente["cpf"] == cpf:
                            tabela = [[chave, valor] for chave, valor in cliente.items()]
                            print(tabulate(tabela, headers="keys", tablefmt="grid"))
                            while True:
                                menu_conta_usuario()
                                opt = input("Opção: ")
                                match opt:
                                    case "a":
                                        conta = buscar_conta_corrente(cliente, contas_corrente)
                                        if conta is None:
                                            print("Nenhuma conta encontrarda! crie uma conta corrente com a opção [c].")
                                            continue
                                        else:
                                            try:
                                                transacoes(cliente, conta)
                                            except ():
                                                print("Erro ao tentar acessar conta corrente!")
                                                continue
                                            else:
                                                print("sucesso!")
                                    case "c":
                                        try:
                                            nova_conta = cadastrar_conta_corrente(cliente["cpf"])
                                        except ():
                                            print("Ocorreu um erro ao tentar cadastrar a conta!")
                                            continue
                                        else:
                                            contas_corrente.append(nova_conta)
                                            dados_conta = {"nro": nova_conta["nro"], "agencia": nova_conta["agencia"]}
                                            cliente["contas"].append(dados_conta)
                                            print(nova_conta)
                                            print("conta cadastrada com sucesso!")
                                    case "q":
                                        print("saindo...")
                                        break
                                    case _:
                                        print("opção inválida!")
                                        continue
                else:
                    print("cpf não encontrado!")
                    continue
            else:
                print("CPF inválido! Tente novamente!")
                continue
            break

    def listar_clientes():
        print(tabulate(clientes, headers="keys", tablefmt="grid"))

    while True:
        menu_usuario()
        opt = input("=> Opção: ")
        match opt:
            case "a":
                try:
                    acessar_usuario()
                except ():
                    print("Erro ao tentar cadastrar cliente!")
                    continue
            case "c":
                try:
                    cliente = cadastro_usuario()
                except ():
                    print("Erro ao tentar cadastrar cliente!")
                    continue
                else:
                    if cliente:
                        cpfs_cadastrados.add(cliente["cpf"])
                        clientes.append(cliente)
                        print("cliente cadastrado com sucesso!")
            case "l":
                if len(clientes) == 0:
                    print("nenhum CPF cadastrado")
                else:
                    listar_clientes()
            case "q":
                print("Fechando sistema...")
                break
            case _:
                print("ERRO! Opção Inválida.")
                continue


area_usuario()
