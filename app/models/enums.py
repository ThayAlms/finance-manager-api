from enum import Enum


class TipoMovimento(str, Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"


class TipoConta(str, Enum):
    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    CARTEIRA = "CARTEIRA"


class Natureza(str, Enum):
    PESSOAL = "PESSOAL"
    NEGOCIO = "NEGOCIO"
