"""Custo padrao dos itens fabricados (RF13)."""

from capacidade import buscar_fabricado
from estrutura import explodir, obter_componentes
from itens import ordenar_codigos
from utils import formatar_moeda, formatar_numero, ler_texto


# ---------- Logica ----------

def multiplicar(quantidade, valor):
    """Multiplica e arredonda para centavos."""
    return round(quantidade * valor, 2)


def calcular_mao_de_obra(dados, codigo):
    """Calcula o custo de mao de obra de uma unidade do item."""
    roteiro = dados["roteiros"].get(codigo)
    if not roteiro:
        return 0
    centro = dados["centros"][roteiro["centro"]]
    return multiplicar(roteiro["tempo"], centro["custo_hora"])


def calcular_materiais(dados, codigo):
    """Soma o custo dos componentes de uma unidade do item."""
    total = 0
    componentes = obter_componentes(dados["estrutura"], codigo)
    for componente, quantidade in componentes.items():
        total += multiplicar(quantidade, calcular_custo(dados, componente))
    return round(total, 2)


def calcular_custo(dados, codigo):
    """Calcula o custo padrao de uma unidade do item."""
    item = dados["itens"][codigo]
    # A materia-prima e comprada: o custo vem do cadastro
    if item["tipo"] == "MP":
        return item["custo"]
    materiais = calcular_materiais(dados, codigo)
    mao_de_obra = calcular_mao_de_obra(dados, codigo)
    return round(materiais + mao_de_obra, 2)


def listar_fabricados(itens):
    """Devolve os codigos dos itens fabricados (PA e SA)."""
    return [
        codigo for codigo in ordenar_codigos(itens)
        if itens[codigo]["tipo"] != "MP"
    ]


def listar_pendencias(dados, codigo):
    """Devolve o que falta cadastrar para o custo ficar completo."""
    pendencias = []
    for _, cod_item, _ in explodir(dados["estrutura"], codigo):
        item = dados["itens"][cod_item]
        if item["tipo"] == "MP":
            if item["custo"] == 0:
                pendencias.append(f"{cod_item} sem custo unitario")
            continue
        if not obter_componentes(dados["estrutura"], cod_item):
            pendencias.append(f"{cod_item} sem estrutura")
        if cod_item not in dados["roteiros"]:
            pendencias.append(f"{cod_item} sem roteiro")
    return pendencias


# ---------- Telas ----------

def exibir_componentes(dados, codigo):
    """Mostra uma linha de custo para cada componente."""
    componentes = obter_componentes(dados["estrutura"], codigo)
    for componente in ordenar_codigos(componentes):
        quantidade = componentes[componente]
        descricao = dados["itens"][componente]["descricao"][:27]
        unitario = calcular_custo(dados, componente)
        total = multiplicar(quantidade, unitario)
        print(
            f"{componente:<8}{descricao:<28}"
            f"{formatar_numero(quantidade):>8}"
            f"{formatar_moeda(unitario):>12}{formatar_moeda(total):>12}"
        )


def exibir_mao_de_obra(dados, codigo):
    """Mostra a linha de mao de obra, se houver roteiro."""
    roteiro = dados["roteiros"].get(codigo)
    if not roteiro:
        return
    centro = dados["centros"][roteiro["centro"]]
    texto = f"Mao de obra {centro['codigo']}"
    horas = f"{formatar_numero(roteiro['tempo'])} h"
    total = calcular_mao_de_obra(dados, codigo)
    print(
        f"{texto:<36}{horas:>8}"
        f"{formatar_moeda(centro['custo_hora']):>12}"
        f"{formatar_moeda(total):>12}"
    )


def tela_detalhar(dados):
    """Tela com o custo padrao detalhado de um item."""
    item = buscar_fabricado(
        dados["itens"], ler_texto("Codigo do item fabricado")
    )
    codigo = item["codigo"]
    print(f"\nCUSTO PADRAO - {codigo} {item['descricao']}")
    print(
        f"{'Item':<8}{'Descricao':<28}{'Qtde':>8}"
        f"{'Custo un.':>12}{'Total':>12}"
    )
    print("-" * 68)
    exibir_componentes(dados, codigo)
    exibir_mao_de_obra(dados, codigo)
    print("-" * 68)
    total = f"R$ {formatar_moeda(calcular_custo(dados, codigo))}"
    print(f"{'CUSTO PADRAO TOTAL':<48}{total:>20}")
    for pendencia in listar_pendencias(dados, codigo):
        print(f"AVISO: {pendencia}.")


def tela_resumo(dados):
    """Tela com o custo padrao de todos os itens fabricados."""
    fabricados = listar_fabricados(dados["itens"])
    if not fabricados:
        print("\nNenhum item fabricado cadastrado.")
        return
    print("\nCUSTO PADRAO DOS ITENS FABRICADOS (R$)")
    print(
        f"{'Item':<8}{'Descricao':<28}{'Materiais':>12}"
        f"{'Mao de obra':>13}{'Custo':>12}"
    )
    print("-" * 73)
    for codigo in fabricados:
        descricao = dados["itens"][codigo]["descricao"][:27]
        materiais = calcular_materiais(dados, codigo)
        mao_de_obra = calcular_mao_de_obra(dados, codigo)
        custo = calcular_custo(dados, codigo)
        print(
            f"{codigo:<8}{descricao:<28}{formatar_moeda(materiais):>12}"
            f"{formatar_moeda(mao_de_obra):>13}"
            f"{formatar_moeda(custo):>12}"
        )
