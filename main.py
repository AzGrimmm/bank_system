from datetime import datetime
import re
from tabulate import tabulate
from classes import system


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


def transacoes(conta):
    @capsula_ambiente("Transações")
    def menu_transacoes():
        dados = """\t[d] Deposito \t[s] Saque
\t[e] Extrato  \t[q] Voltar"""
        print(f"Saldo atual: R${conta._saldo:.2f}")
        print(dados)

    @capsula_ambiente("Extrato")
    def extrato():
        """Exibe o saldo atual e as transações realizadas."""
        dados = [[transacao["tipo"], transacao["valor"], transacao["data"]] for transacao in conta._historico.transacoes]
        print(f"Saldo atual: R${conta._saldo:.2f}")
        print(tabulate(dados, headers=["Tipo", "Valor", "Data"], tablefmt="grid"))

    while True:
        menu_transacoes()
        opt = input("=> Opção: ")
        if opt == "d":
            try:
                valor = float(input("Valor: R$"))
                system.Deposito(valor).registrar(conta)
            except (ValueError):
                print("Operação falhou! valor inválido!")
        elif opt == "s":
            excedeu_limite_saques = conta.numero_saques >= conta.LIMITE_SAQUES
            if conta._saldo <= 0:
                print("Operação falhou! Sem Saldo")
                continue
            elif excedeu_limite_saques:
                print(f"Operação falhou! => Limite de {conta.LIMITE_SAQUES} saques diários alcançado!")
                continue
            try:
                valor = float(input("Valor: R$"))
                system.Saque(valor).registrar(conta)
            except (ValueError):
                print("Operação falhou! valor inválido!")
        elif opt == "e":
            try:
                extrato()
            except ():
                print("Erro ao tentar exibir o extrato!")
        elif opt == "q":
            print("Fechando sistema de transações...")
            break
        else:
            print("ERRO! Escolha uma opção válida!")


def buscar_conta_corrente(cliente):
    if len(cliente.contas) == 0:
        return None
    else:
        for i, c in enumerate(cliente.contas):
            print(f"[{i}] - Número da conta: {c.numero} Agência: {c.agencia}")

        while True:
            try:
                conta_escolhida = int(input("Qual conta quer acessar?: "))
                if 0 <= conta_escolhida < len(cliente.contas):
                    return cliente.contas[conta_escolhida]
                else:
                    print("Índice inválido. Tente novamente.")
            except ValueError:
                print("Entrada inválida! Digite um número válido.")


def main():
    clientes = []
    contas_corrente = []

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
\t[c] - cadastrar conta corrente
\t[q] - sair
"""
        print(menu)

    def validar_nome_completo(nome_completo):
        nome_completo = nome_completo.strip()
        if len(nome_completo.split()) < 2:
            return False
        if not all(palavra.isalpha() for palavra in nome_completo.split()):
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
        padrao = r"^([\w\s\.]+) - (\d+\w?) - ([\w\s]+) - ([\w\s]+)\/([a-zA-Z]{2})$"

        match = re.match(padrao, endereco)

        if match:
            logradouro, nro, bairro, cidade, sigla_estado = match.groups()

            # Verificações adicionais
            if len(sigla_estado) != 2:  # UF deve ter 2 letras
                print("Sigla inválida")
                return False

            return True
        return False

    def filtrar_cliente(cpf, clientes):
        clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    @capsula_ambiente("Cadastro de usuário")
    def cadastrar_usuario():
        cliente = {}

        while True:
            while True:
                cpf = pedir_dado("CPF ('s' para sair): ")
                if cpf is None:
                    return False
                if not validar_cpf(cpf):
                    print("CPF inválido! Tente novamente!")
                    continue

                elif filtrar_cliente(cpf, clientes):  # Só verifica se o CPF já existe depois de validar
                    print("CPF já cadastrado! Tente novamente!")
                    continue
                else:
                    cliente["cpf"] = cpf  # Agora só chega aqui se o CPF for válido e ainda não existir
                    break  # Sai do loop após um CPF válido ser cadastrado
            while True:
                nome = pedir_dado("Nome Completo ('s' para sair): ")
                if nome is None:
                    return False
                if not validar_nome_completo(nome):
                    print("Nome Completo inválido")
                    continue
                cliente["nome"] = nome.title()
                break
            while True:
                dia_nasc = pedir_dado("Dia do nascimento ('s' para sair): ")
                if dia_nasc is None:
                    return False
                mes_nasc = pedir_dado("Mês do nascimento ('s' para sair): ")
                if mes_nasc is None:
                    return False
                ano_nasc = pedir_dado("Ano do nascimento ('s' para sair): ")
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
                print("Endereço:")
                logradouro = pedir_dado("Logradouro ('s' para sair): ")
                if logradouro is None:
                    return False
                nro = pedir_dado("nro ('s' para sair): ")
                if nro is None:
                    return False
                bairro = pedir_dado("bairro ('s' para sair): ")
                if bairro is None:
                    return False
                cidade = pedir_dado("cidade ('s' para sair): ")
                if cidade is None:
                    return False
                sigla_estado = pedir_dado("estado(sigla) ('s' para sair): ")
                if sigla_estado is None:
                    return False
                endereco = f"{logradouro} - {nro} - {bairro} - {cidade}/{sigla_estado}"
                validacao = validar_endereco(endereco)
                if validacao:
                    cliente["endereco"] = endereco.title()
                    break
                else:
                    print("Endereço inválido!")
                    continue
            break
        obj_cliente = system.PessoaFisica(cliente["nome"], cliente["cpf"], cliente["nascimento"], cliente["endereco"])
        clientes.append(obj_cliente)
        return obj_cliente if obj_cliente else {}

    @capsula_ambiente("Acesso ao usuário")
    def acessar_usuario():
        while True:
            cpf = pedir_dado("CPF - 's' para sair: ")
            if cpf is None:
                break
            if validar_cpf(cpf):
                cliente = filtrar_cliente(cpf, clientes)
                if not cliente:
                    print("Cliente não encontrado!")
                    break
                else:
                    print(f"Olá {cliente.nome.split(" ")[0]}")
                    while True:
                        menu_conta_usuario()
                        opt = input("Opção: ")
                        match opt:
                            case "a":
                                conta = buscar_conta_corrente(cliente)
                                if conta is None:
                                    print("Nenhuma conta encontrarda! crie uma conta corrente com a opção [c].")
                                    continue
                                else:
                                    try:
                                        transacoes(conta)
                                    except ():
                                        print("Erro ao tentar acessar conta corrente!")
                                        continue
                            case "c":
                                try:
                                    conta = system.ContaCorrente.nova_conta(cliente, len(contas_corrente) + 1)
                                except ():
                                    print("Ocorreu um erro ao tentar cadastrar a conta!")
                                    continue
                                else:
                                    contas_corrente.append(conta)
                                    cliente.contas.append(conta)
                                    print("conta cadastrada com sucesso!")
                            case "q":
                                print("saindo...")
                                break
                            case _:
                                print("opção inválida!")
                                continue
            else:
                print("CPF inválido! Tente novamente!")
                continue
            break

    def listar_clientes():
        dados = [[c.nome, c.cpf, c.nascimento, c.endereco] for c in clientes]
        print(tabulate(dados, headers=["Nome", "CPF", "nascimento", "Endereço"], tablefmt="grid"))

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
                    cliente = cadastrar_usuario()
                    if cliente:
                        print(f"cliente {cliente.nome.split(" ")[0]} cadastrado com sucesso!")
                except ():
                    print("Erro ao tentar cadastrar cliente!")
                    continue
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


main()
