"""Exportacao de relatorios em CSV (RF14)."""

import csv

from custos import calcular_custo
from estoque import abaixo_da_seguranca, obter_saldo
from itens import ordenar_codigos
from utils import caminho_saida, formatar_moeda, formatar_numero

CABECALHO_ESTOQUE = (
    "Codigo", "Descricao", "Tipo", "Unidade", "Saldo",
    "Estoque de seguranca", "Situacao", "Custo unitario", "Valor total",
)
CABECALHO_ORDENS = (
    "Numero", "Tipo", "Item", "Descricao", "Quantidade",
    "Semana de liberacao", "Semana de entrega", "Status", "Atrasada",
)


# ---------- Logica ----------

def montar_linha_estoque(dados, codigo):
    """Monta a linha de um item na posicao de estoque."""
    item = dados["itens"][codigo]
    saldo = obter_saldo(dados["estoque"], codigo)
    custo = calcular_custo(dados, codigo)
    abaixo = abaixo_da_seguranca(dados["estoque"], item)
    return [
        codigo,
        item["descricao"],
        item["tipo"],
        item["unidade"],
        formatar_numero(saldo),
        formatar_numero(item["estoque_seguranca"]),
        "ABAIXO" if abaixo else "OK",
        formatar_moeda(custo),
        formatar_moeda(saldo * custo),
    ]


def montar_linha_ordem(dados, ordem):
    """Monta a linha de uma ordem no relatorio de ordens."""
    return [
        ordem["numero"],
        ordem["tipo"],
        ordem["codigo"],
        dados["itens"][ordem["codigo"]]["descricao"],
        formatar_numero(ordem["quantidade"]),
        ordem["semana_liberacao"],
        ordem["semana_entrega"],
        ordem["status"],
        "SIM" if ordem["atrasada"] else "NAO",
    ]


def gravar_csv(nome, cabecalho, linhas):
    """Grava um arquivo CSV e devolve o caminho dele."""
    try:
        caminho = caminho_saida(nome)
        with open(
            caminho, "w", newline="", encoding="utf-8-sig"
        ) as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(cabecalho)
            escritor.writerows(linhas)
    except OSError as erro:
        raise ValueError(
            f"nao foi possivel gravar {nome}. "
            "Feche o arquivo, se ele estiver aberto."
        ) from erro
    return caminho


def exportar_estoque(dados):
    """Exporta a posicao de estoque e devolve o caminho do arquivo."""
    linhas = [
        montar_linha_estoque(dados, codigo)
        for codigo in ordenar_codigos(dados["itens"])
    ]
    return gravar_csv("posicao_estoque.csv", CABECALHO_ESTOQUE, linhas)


def exportar_ordens(dados):
    """Exporta a lista de ordens e devolve o caminho do arquivo."""
    linhas = [
        montar_linha_ordem(dados, ordem) for ordem in dados["ordens"]
    ]
    return gravar_csv("lista_ordens.csv", CABECALHO_ORDENS, linhas)


# ---------- Telas ----------

def tela_estoque(dados):
    """Tela que exporta a posicao de estoque."""
    if not dados["itens"]:
        print("\nNenhum item cadastrado.")
        return
    caminho = exportar_estoque(dados)
    print(f"\n{len(dados['itens'])} item(ns) exportado(s) para:")
    print(caminho)


def tela_ordens(dados):
    """Tela que exporta a lista de ordens."""
    if not dados["ordens"]:
        print("\nNenhuma ordem cadastrada.")
        return
    caminho = exportar_ordens(dados)
    print(f"\n{len(dados['ordens'])} ordem(ns) exportada(s) para:")
    print(caminho)
