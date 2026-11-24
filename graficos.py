"""Graficos de gestao com matplotlib (RF16)."""

from capacidade import buscar_centro, calcular_carga, listar_sobrecargas
from estoque import abaixo_da_seguranca, obter_saldo
from itens import buscar_item, ordenar_codigos
from mps import SEMANAS
from mrp import calcular_mrp
from utils import caminho_saida, formatar_numero, ler_texto

# O restante do sistema funciona mesmo sem o matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
except ImportError:
    plt = None

AZUL = "#2a78d6"
LARANJA = "#eb6834"
VERMELHO = "#d03b3b"
CINZA = "#b5b4ac"
ESCURO = "#52514e"
GRADE = "#e1e0d9"
EIXO_SEMANAS = range(1, SEMANAS + 1)


# ---------- Apoio ----------

def verificar_biblioteca():
    """Avisa se o matplotlib nao estiver instalado."""
    if plt is None:
        raise ValueError(
            "matplotlib nao instalado. "
            "Execute: python -m pip install matplotlib"
        )


def formatar_eixo(valor, _):
    """Formata os numeros dos eixos com virgula."""
    return formatar_numero(valor)


def criar_figura(titulo, rotulo_x, rotulo_y, altura=5):
    """Cria uma figura com o estilo padrao do sistema."""
    figura, eixo = plt.subplots(figsize=(9, altura))
    eixo.set_title(titulo, loc="left")
    eixo.set_xlabel(rotulo_x)
    eixo.set_ylabel(rotulo_y)
    eixo.spines[["top", "right"]].set_visible(False)
    eixo.grid(axis="y", color=GRADE)
    eixo.set_axisbelow(True)
    eixo.yaxis.set_major_formatter(formatar_eixo)
    return figura, eixo


def colocar_legenda(eixo, simbolos=None):
    """Coloca a legenda abaixo do grafico."""
    eixo.legend(
        handles=simbolos, loc="upper center",
        bbox_to_anchor=(0.5, -0.12), ncols=3, frameon=False,
    )


def finalizar(figura, nome):
    """Salva a figura em PNG e mostra na tela."""
    figura.tight_layout()
    try:
        caminho = caminho_saida(nome)
        figura.savefig(caminho, dpi=150)
        print(f"\nGrafico salvo em:\n{caminho}")
        print("Feche a janela do grafico para continuar.")
        plt.show()
    except OSError as erro:
        raise ValueError(f"nao foi possivel gravar {nome}.") from erro
    finally:
        plt.close(figura)


def contar_ordens(ordens, tipo):
    """Conta, por semana de entrega, as ordens em aberto do tipo."""
    contagem = [0] * SEMANAS
    for ordem in ordens:
        if ordem["tipo"] == tipo and ordem["status"] != "ENCERRADA":
            contagem[ordem["semana_entrega"] - 1] += 1
    return contagem


# ---------- Graficos ----------

def desenhar_estoque(dados):
    """Barras com o saldo e o estoque de seguranca de cada item."""
    itens, estoque = dados["itens"], dados["estoque"]
    codigos = ordenar_codigos(itens)
    posicoes = range(len(codigos))
    saldos = [obter_saldo(estoque, codigo) for codigo in codigos]
    segurancas = [itens[cod]["estoque_seguranca"] for cod in codigos]
    cores = [
        VERMELHO if abaixo_da_seguranca(estoque, itens[codigo]) else AZUL
        for codigo in codigos
    ]
    figura, eixo = criar_figura(
        "Posicao de estoque: saldo x estoque de seguranca",
        "Quantidade (escala logaritmica)", "", altura=8,
    )
    barras = eixo.barh(
        [pos - 0.2 for pos in posicoes], saldos, height=0.36, color=cores
    )
    eixo.barh(
        [pos + 0.2 for pos in posicoes], segurancas, height=0.36,
        color=CINZA,
    )
    textos = [formatar_numero(saldo) for saldo in saldos]
    eixo.bar_label(barras, textos, padding=3)
    eixo.set_yticks(posicoes, codigos)
    eixo.invert_yaxis()
    # A escala logaritmica deixa ver valores muito diferentes
    eixo.set_xscale("symlog")
    eixo.xaxis.set_major_formatter(formatar_eixo)
    legenda = [
        Patch(color=AZUL, label="Saldo"),
        Patch(color=CINZA, label="Estoque de seguranca"),
    ]
    if VERMELHO in cores:
        legenda.append(Patch(color=VERMELHO, label="Saldo abaixo"))
    colocar_legenda(eixo, legenda)
    eixo.grid(visible=False, axis="y")
    return figura


def desenhar_projetado(dados, item):
    """Linha do estoque projetado com o estoque de seguranca."""
    codigo = item["codigo"]
    projetado = calcular_mrp(dados)[codigo]["projetado"]
    figura, eixo = criar_figura(
        f"Estoque projetado - {codigo} {item['descricao']}",
        "Semana", f"Quantidade ({item['unidade']})",
    )
    eixo.plot(
        EIXO_SEMANAS, projetado, color=AZUL, linewidth=2, marker="o",
        markersize=8, label="Estoque projetado",
    )
    eixo.axhline(
        item["estoque_seguranca"], color=ESCURO, linestyle="--",
        label="Estoque de seguranca",
    )
    eixo.set_ylim(bottom=0)
    eixo.set_xticks(EIXO_SEMANAS)
    colocar_legenda(eixo)
    return figura


def desenhar_ordens(dados):
    """Barras empilhadas com as OPs e OCs por semana de entrega."""
    producao = contar_ordens(dados["ordens"], "OP")
    compra = contar_ordens(dados["ordens"], "OC")
    figura, eixo = criar_figura(
        "Ordens em aberto por semana de entrega",
        "Semana de entrega", "Quantidade de ordens",
    )
    eixo.bar(
        EIXO_SEMANAS, producao, width=0.5, color=AZUL,
        edgecolor="white", linewidth=1.5, label="Producao (OP)",
    )
    eixo.bar(
        EIXO_SEMANAS, compra, width=0.5, bottom=producao, color=LARANJA,
        edgecolor="white", linewidth=1.5, label="Compra (OC)",
    )
    eixo.yaxis.get_major_locator().set_params(integer=True)
    eixo.set_xticks(EIXO_SEMANAS)
    colocar_legenda(eixo)
    return figura


def desenhar_carga(dados, centro):
    """Barras da carga semanal com a linha da capacidade."""
    capacidade = centro["capacidade"]
    cargas = calcular_carga(dados, centro["codigo"])
    sobrecargas = listar_sobrecargas(cargas, capacidade)
    cores = [
        VERMELHO if semana in sobrecargas else AZUL
        for semana in EIXO_SEMANAS
    ]
    figura, eixo = criar_figura(
        f"Carga x capacidade - {centro['codigo']} {centro['descricao']}",
        "Semana de liberacao", "Horas",
    )
    barras = eixo.bar(EIXO_SEMANAS, cargas, width=0.5, color=cores)
    textos = [
        f"{formatar_numero(carga)} h" if carga > capacidade else ""
        for carga in cargas
    ]
    eixo.bar_label(barras, textos, padding=3)
    linha = eixo.axhline(
        capacidade, color=ESCURO, linestyle="--", label="Capacidade"
    )
    legenda = [Patch(color=AZUL, label="Carga"), linha]
    if sobrecargas:
        legenda.append(Patch(color=VERMELHO, label="Sobrecarga"))
    eixo.set_xticks(EIXO_SEMANAS)
    colocar_legenda(eixo, legenda)
    return figura


# ---------- Telas ----------

def tela_estoque(dados):
    """Tela do grafico de posicao de estoque."""
    verificar_biblioteca()
    if not dados["itens"]:
        print("\nNenhum item cadastrado.")
        return
    finalizar(desenhar_estoque(dados), "grafico_estoque.png")


def tela_projetado(dados):
    """Tela do grafico de estoque projetado de um item."""
    verificar_biblioteca()
    item = buscar_item(dados["itens"], ler_texto("Codigo do item"))
    nome = f"grafico_projetado_{item['codigo']}.png"
    finalizar(desenhar_projetado(dados, item), nome)


def tela_ordens(dados):
    """Tela do grafico de ordens por semana de entrega."""
    verificar_biblioteca()
    if not dados["ordens"]:
        print("\nNenhuma ordem cadastrada. Execute o MRP.")
        return
    finalizar(desenhar_ordens(dados), "grafico_ordens.png")


def tela_carga(dados):
    """Tela do grafico de carga x capacidade de um centro."""
    verificar_biblioteca()
    centro = buscar_centro(
        dados["centros"], ler_texto("Codigo do centro (ex.: CT-01)")
    )
    nome = f"grafico_carga_{centro['codigo']}.png"
    finalizar(desenhar_carga(dados, centro), nome)
