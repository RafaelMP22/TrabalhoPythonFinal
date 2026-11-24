"""Leitura e gravacao dos dados em arquivos (RF15 e RNF07)."""

import csv
import json
from pathlib import Path

PASTA_DADOS = Path(__file__).parent / "data"

# Nome de cada arquivo JSON e o tipo de dado que ele guarda
ARQUIVOS_JSON = {
    "itens": dict,
    "estrutura": dict,
    "estoque": dict,
    "centros": dict,
    "roteiros": dict,
    "mps": dict,
    "ordens": list,
}
CAMPOS_MOVIMENTO = (
    "data", "codigo", "tipo", "quantidade", "saldo", "documento",
)


# ---------- Leitura ----------

def ler_json(nome, tipo):
    """Le um arquivo JSON; se ele nao existir, devolve um dado vazio."""
    caminho = PASTA_DADOS / f"{nome}.json"
    if not caminho.exists():
        return tipo()
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (OSError, ValueError) as erro:
        raise ValueError(f"nao foi possivel ler {caminho}.") from erro
    if not isinstance(conteudo, tipo):
        raise ValueError(f"conteudo inesperado em {caminho}.")
    return conteudo


def converter_movimento(linha):
    """Converte os textos do CSV nos tipos certos."""
    movimento = {campo: linha[campo] for campo in CAMPOS_MOVIMENTO}
    movimento["quantidade"] = float(movimento["quantidade"])
    movimento["saldo"] = float(movimento["saldo"])
    return movimento


def ler_movimentos():
    """Le o historico de movimentos do arquivo CSV."""
    caminho = PASTA_DADOS / "movimentos.csv"
    if not caminho.exists():
        return []
    try:
        with open(caminho, newline="", encoding="utf-8-sig") as arquivo:
            linhas = csv.DictReader(arquivo, delimiter=";")
            return [converter_movimento(linha) for linha in linhas]
    except (OSError, KeyError, TypeError, ValueError) as erro:
        raise ValueError(f"nao foi possivel ler {caminho}.") from erro


def carregar_dados():
    """Le todos os arquivos e monta o dicionario de dados."""
    dados = {
        nome: ler_json(nome, tipo)
        for nome, tipo in ARQUIVOS_JSON.items()
    }
    dados["movimentos"] = ler_movimentos()
    return dados


# ---------- Gravacao ----------

def gravar_json(nome, conteudo):
    """Grava um arquivo JSON, sem risco de deixa-lo pela metade."""
    temporario = PASTA_DADOS / f"{nome}.tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
    # So troca o arquivo antigo depois de gravar o novo inteiro
    temporario.replace(PASTA_DADOS / f"{nome}.json")


def gravar_movimentos(movimentos):
    """Grava o historico de movimentos no arquivo CSV."""
    temporario = PASTA_DADOS / "movimentos.tmp"
    with open(
        temporario, "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=CAMPOS_MOVIMENTO, delimiter=";"
        )
        escritor.writeheader()
        escritor.writerows(movimentos)
    temporario.replace(PASTA_DADOS / "movimentos.csv")


def salvar_dados(dados):
    """Grava todos os dados na pasta data."""
    try:
        PASTA_DADOS.mkdir(exist_ok=True)
        # O historico vem primeiro: se falhar, o saldo nao e gravado
        gravar_movimentos(dados["movimentos"])
        for nome in ARQUIVOS_JSON:
            gravar_json(nome, dados[nome])
    except OSError as erro:
        raise ValueError(
            "nao foi possivel salvar os dados. Feche os arquivos da "
            "pasta data, se estiverem abertos."
        ) from erro
