"""Validacoes de entrada e formatacao de valores (RNF05)."""

import math
from datetime import date
from pathlib import Path

# Pasta dos relatorios e graficos
PASTA_SAIDA = Path(__file__).parent / "docs"


def montar_mensagem(rotulo, atual):
    """Monta o texto da pergunta, mostrando o valor atual se houver."""
    if atual is None:
        return f"{rotulo}: "
    return f"{rotulo} [{atual}]: "


def formatar_numero(valor):
    """Formata um numero com virgula e sem zeros sobrando."""
    texto = f"{valor:.3f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def formatar_moeda(valor):
    """Formata um valor com duas casas decimais e virgula."""
    return f"{valor:.2f}".replace(".", ",")


def data_hoje():
    """Devolve a data de hoje no formato dia/mes/ano."""
    return date.today().strftime("%d/%m/%Y")


def formatar_colunas(valores, largura):
    """Coloca varios numeros lado a lado, em colunas alinhadas."""
    return "".join(
        f"{formatar_numero(valor):>{largura}}" for valor in valores
    )


def caminho_saida(nome):
    """Devolve o caminho de um arquivo na pasta de saida."""
    PASTA_SAIDA.mkdir(exist_ok=True)
    return PASTA_SAIDA / nome


def ler_texto(rotulo, atual=None):
    """Le um texto que nao pode ficar vazio."""
    while True:
        texto = input(montar_mensagem(rotulo, atual)).strip()
        if texto:
            return texto
        if atual is not None:
            return atual
        print("ERRO: este campo e obrigatorio.")


def ler_escolha(rotulo, opcoes):
    """Le uma das opcoes permitidas."""
    while True:
        texto = input(f"{rotulo}: ").strip().upper()
        if texto in opcoes:
            return texto
        print(f"ERRO: escolha entre {', '.join(opcoes)}.")


def ler_inteiro(rotulo, atual=None, minimo=0):
    """Le um numero inteiro maior ou igual ao minimo."""
    while True:
        texto = input(montar_mensagem(rotulo, atual)).strip()
        if not texto and atual is not None:
            return atual
        try:
            numero = int(texto)
        except ValueError:
            print("ERRO: digite um numero inteiro.")
            continue
        if numero < minimo:
            print(f"ERRO: o valor minimo e {minimo}.")
            continue
        return numero


def ler_decimal(rotulo, atual=None, minimo=0):
    """Le um numero decimal maior ou igual ao minimo."""
    exibido = None if atual is None else formatar_numero(atual)
    while True:
        texto = input(montar_mensagem(rotulo, exibido)).strip()
        if not texto and atual is not None:
            return atual
        try:
            numero = float(texto.replace(",", "."))
        except ValueError:
            print("ERRO: digite um numero (ex.: 10 ou 0,5).")
            continue
        # Recusa valores especiais, como "nan" e "inf"
        if not math.isfinite(numero):
            print("ERRO: digite um numero (ex.: 10 ou 0,5).")
            continue
        if numero < minimo:
            print(f"ERRO: o valor minimo e {formatar_numero(minimo)}.")
            continue
        return numero
