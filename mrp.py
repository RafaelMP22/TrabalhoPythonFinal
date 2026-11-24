"""Calculo MRP e registro por item (RF08 e RN04 a RN08)."""

from estoque import CASAS_DECIMAIS, obter_saldo
from estrutura import obter_componentes
from itens import buscar_item, ordenar_codigos
from mps import SEMANAS, obter_demanda
from ordens import exibir_ordens, substituir_planejadas
from utils import data_hoje, formatar_colunas, formatar_numero, ler_texto

# Status que contam como recebimento programado (RN08)
STATUS_PROGRAMADOS = ("FIRME", "LIBERADA")
LARGURA_COLUNA = 7

# Texto exibido e chave de cada linha do registro
LINHAS_REGISTRO = (
    ("Necessidade bruta", "bruta"),
    ("Receb. programados", "programado"),
    ("Estoque projetado", "projetado"),
    ("Necessidade liquida", "liquida"),
    ("Receb. planejados", "planejado"),
    ("Liberacao planejada", "liberacao"),
)


# ---------- Logica ----------

def arredondar(valor):
    """Arredonda para evitar sobras nos numeros decimais."""
    return round(valor, CASAS_DECIMAIS)


def somar_programados(ordens, codigo):
    """Soma, por semana, as ordens firmes e liberadas do item (RN08)."""
    programados = [0] * SEMANAS
    for ordem in ordens:
        if ordem["codigo"] != codigo:
            continue
        if ordem["status"] in STATUS_PROGRAMADOS:
            programados[ordem["semana_entrega"] - 1] += ordem["quantidade"]
    return programados


def calcular_lote(liquida, lote_minimo):
    """Devolve a quantidade a receber (RN06)."""
    if liquida == 0:
        return 0
    return max(liquida, lote_minimo)


def calcular_liberacoes(planejados, lead_time):
    """Antecipa os recebimentos pelo lead time (RN07)."""
    liberacoes = [0] * SEMANAS
    for posicao, quantidade in enumerate(planejados):
        destino = posicao - lead_time
        # Antes da semana 1 a liberacao fica fora do quadro
        if destino >= 0:
            liberacoes[destino] = quantidade
    return liberacoes


def calcular_registro(item, brutas, programados, saldo):
    """Calcula as seis linhas do registro MRP de um item."""
    projetados, liquidas, planejados = [], [], []
    anterior = saldo
    for bruta, programado in zip(brutas, programados):
        disponivel = anterior + programado
        # RN05: necessidade liquida da semana
        falta = bruta + item["estoque_seguranca"] - disponivel
        liquida = max(0, arredondar(falta))
        planejado = calcular_lote(liquida, item["lote_minimo"])
        anterior = arredondar(disponivel + planejado - bruta)
        liquidas.append(liquida)
        planejados.append(planejado)
        projetados.append(anterior)
    return {
        "saldo": saldo,
        "bruta": brutas,
        "programado": programados,
        "projetado": projetados,
        "liquida": liquidas,
        "planejado": planejados,
        "liberacao": calcular_liberacoes(planejados, item["lead_time"]),
    }


def somar_necessidade(brutas, liberacoes, quantidade):
    """Soma a necessidade gerada por um pai no componente (RN04)."""
    for posicao, liberacao in enumerate(liberacoes):
        brutas[posicao] = arredondar(
            brutas[posicao] + liberacao * quantidade
        )


def iniciar_brutas(dados):
    """Comeca com a demanda do MPS nos PA e zero nos demais itens."""
    return {
        codigo: list(obter_demanda(dados["mps"], codigo))
        for codigo in dados["itens"]
    }


def calcular_mrp(dados):
    """Calcula o registro MRP de todos os itens, na ordem da RN04."""
    brutas = iniciar_brutas(dados)
    registros = {}
    for codigo in ordenar_codigos(dados["itens"]):
        registro = calcular_registro(
            dados["itens"][codigo],
            brutas[codigo],
            somar_programados(dados["ordens"], codigo),
            obter_saldo(dados["estoque"], codigo),
        )
        registros[codigo] = registro
        # Passa a necessidade para os componentes diretos
        componentes = obter_componentes(dados["estrutura"], codigo)
        for componente, quantidade in componentes.items():
            somar_necessidade(
                brutas[componente], registro["liberacao"], quantidade
            )
    return registros


def listar_sugestoes(itens, registros):
    """Transforma os recebimentos planejados em sugestoes de ordem."""
    sugestoes = []
    for codigo, registro in registros.items():
        for posicao, quantidade in enumerate(registro["planejado"]):
            if quantidade == 0:
                continue
            entrega = posicao + 1
            liberacao = entrega - itens[codigo]["lead_time"]
            sugestoes.append({
                "codigo": codigo,
                "quantidade": quantidade,
                "semana_liberacao": liberacao,
                "semana_entrega": entrega,
                "atrasada": liberacao < 1,
            })
    return sugestoes


# ---------- Telas ----------


def exibir_excecoes(ordens):
    """Mostra as mensagens de excecao das ordens atrasadas (RN07)."""
    atrasadas = [ordem for ordem in ordens if ordem["atrasada"]]
    print(f"\n{len(atrasadas)} mensagem(ns) de excecao.")
    for ordem in atrasadas:
        print(
            f"EXCECAO: {ordem['numero']} ({ordem['codigo']}) deveria ser "
            f"liberada na semana {ordem['semana_liberacao']}."
        )


def tela_executar(dados):
    """Tela que executa o MRP e gera as ordens planejadas (RF09)."""
    registros = calcular_mrp(dados)
    sugestoes = listar_sugestoes(dados["itens"], registros)
    planejadas = substituir_planejadas(dados, sugestoes)
    if not planejadas:
        print("\nMRP executado: nenhuma ordem necessaria.")
        return
    print(f"\nORDENS PLANEJADAS - execucao do MRP em {data_hoje()}")
    exibir_ordens(planejadas)
    exibir_excecoes(planejadas)


def tela_registro(dados):
    """Tela com o registro MRP de um item."""
    item = buscar_item(dados["itens"], ler_texto("Codigo do item"))
    registro = calcular_mrp(dados)[item["codigo"]]
    seguranca = formatar_numero(item["estoque_seguranca"])
    lote = formatar_numero(item["lote_minimo"])
    saldo = formatar_numero(registro["saldo"])
    print(f"\nREGISTRO MRP - {item['codigo']} {item['descricao']}")
    print(
        f"Lead time: {item['lead_time']} sem | "
        f"Est. seguranca: {seguranca} | Lote min.: {lote} | "
        f"Estoque: {saldo}"
    )
    semanas = formatar_colunas(range(1, SEMANAS + 1), LARGURA_COLUNA)
    print(f"\n{'Semana':<20}{semanas}")
    print("-" * 76)
    for texto, chave in LINHAS_REGISTRO:
        valores = formatar_colunas(registro[chave], LARGURA_COLUNA)
        print(f"{texto:<20}{valores}")
