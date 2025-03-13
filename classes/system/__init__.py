from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.nascimento = nascimento


class Conta:
    def __init__(self, cliente, numero):
        self._saldo = 0.0
        self._numero = numero
        self._cliente = cliente
        self._agencia = "0001"
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)

    @property
    def cpf(self):
        return self.cpf

    @property
    def saldo(self):
        return self._saldo

    @property
    def agencia(self):
        return self._agencia

    @property
    def numero(self):
        return self._numero

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = saldo < valor
        if excedeu_saldo:
            print("Operação falhou! => saldo insuficiênte.")
            return False
        elif valor > 0:
            self._saldo -= valor
            print("Operação realizada com sucesso!")
            return True
        else:
            print("Operação falhou! => valor informado inválido!")

    def depositar(self, valor):
        if valor <= 0:
            print("Operação falhou! => valor informado inválido.")
            return False
        else:
            self._saldo += valor
            print("Operação realizada com sucesso!")
            return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, LIMITE_POR_SAQUE=500, LIMITE_SAQUES=3, LIMITE_SAQUE_DIA=1500):
        super().__init__(numero, cliente)
        self.LIMITE_POR_SAQUE = LIMITE_POR_SAQUE
        self.LIMITE_SAQUES = LIMITE_SAQUES
        self.LIMITE_SAQUE_DIA = LIMITE_SAQUE_DIA
        self.soma_saques_diarios = 0

    @property
    def numero_saques(self):
        return len([transacao for transacao in self._historico.transacoes if transacao["tipo"] == "Saque"])

    def sacar(self, valor):
        excedeu_limite_por_saque = valor > self.LIMITE_POR_SAQUE
        excedeu_limite_saque_dia = valor + self.soma_saques_diarios > self.LIMITE_SAQUE_DIA

        if excedeu_limite_por_saque:
            print("Saque limitado a R$500 por operação.")
        elif excedeu_limite_saque_dia:
            print(f"O valor excede o limite diário de R${self.LIMITE_SAQUE_DIA}.")
        else:
            self.soma_saques_diarios = valor
            return super().sacar(valor)


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })


class Transacao(ABC):
    def __init__(self, valor):
        self.valor = valor

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
