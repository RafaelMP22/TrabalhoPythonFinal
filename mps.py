"""Plano Mestre de Producao - MPS (RF07)."""

from itens import buscar_item, ordenar_codigos
from utils import formatar_colunas, ler_inteiro, ler_texto

SEMANAS = 8
LARGURA_COLUNA = 5


# ---------- Logica ----------

def buscar_produto(itens, codigo):
    """Devolve um item que pode entrar no MPS (somente PA)."""
    produto = buscar_item(itens, codigo)
    if produto["tipo"] != "PA":
        raise ValueError(
            f"{produto['codigo']} nao e um produto acabado (PA)."
        )
    return produto


def listar_produtos(itens):
    """Devolve os codigos dos produtos acabados."""
    return [
        codigo for codigo in ordenar_codigos(itens)
        if itens[codigo]["tipo"] == "PA"
    ]


def obter_demanda(mps, codigo):
    """Devolve a demanda semanal de um produto (zeros se nao houver)."""
    return mps.get(codigo, [0] * SEMANAS)


def gravar_demanda(itens, mps, codigo, demanda):
    """Inclui ou altera a demanda semanal de um produto."""
    produto = buscar_produto(itens, codigo)
    if len(demanda) != SEMANAS:
        raise ValueError(f"informe a demanda das {SEMANAS} semanas.")
    if min(demanda) < 0:
        raise ValueError("a demanda nao pode ser negativa.")
    mps[produto["codigo"]] = list(demanda)


# ---------- Telas ----------

def ler_demanda(atual):
    """Le a demanda de cada semana, mostrando o valor atual."""
    demanda = []
    for semana, valor in enumerate(atual, start=1):
        demanda.append(ler_inteiro(f"Semana {semana}", valor))
    return demanda


def exibir_tabela(dados, codigos):
    """Mostra a demanda semanal dos produtos informados."""
    numeros = formatar_colunas(range(1, SEMANAS + 1), LARGURA_COLUNA)
    print(f"{'Codigo':<8}{'Descricao':<21}{numeros}{'Total':>7}")
    print("-" * 76)
    for codigo in codigos:
        demanda = obter_demanda(dados["mps"], codigo)
        descricao = dados["itens"][codigo]["descricao"][:20]
        valores = formatar_colunas(demanda, LARGURA_COLUNA)
        print(f"{codigo:<8}{descricao:<21}{valores}{sum(demanda):>7}")


def tela_cadastrar(dados):
    """Tela de cadastro e alteracao da demanda de um produto."""
    print("\nDEMANDA SEMANAL (ENTER mantem o valor, Ctrl+C cancela)")
    produto = buscar_produto(
        dados["itens"], ler_texto("Codigo do produto")
    )
    codigo = produto["codigo"]
    print(f"{codigo} {produto['descricao']}")
    demanda = ler_demanda(obter_demanda(dados["mps"], codigo))
    gravar_demanda(dados["itens"], dados["mps"], codigo, demanda)
    print("\nDemanda gravada com sucesso.\n")
    exibir_tabela(dados, [codigo])


def tela_exibir(dados):
    """Tela com o plano mestre de todos os produtos."""
    produtos = listar_produtos(dados["itens"])
    if not produtos:
        print("\nNenhum produto acabado cadastrado.")
        return
    print("\nPLANO MESTRE DE PRODUCAO - demanda por semana")
    exibir_tabela(dados, produtos)
