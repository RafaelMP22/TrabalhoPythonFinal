"""Movimentacoes, saldo e kardex (RF04, RF05, RN02 e RN10)."""

from itens import buscar_item
from utils import (
    data_hoje,
    formatar_numero,
    ler_decimal,
    ler_escolha,
    ler_texto,
)

TIPOS_MOVIMENTO = {"E": "ENTRADA", "S": "SAIDA", "A": "AJUSTE"}
CASAS_DECIMAIS = 3
SEM_MINIMO = float("-inf")


# ---------- Logica ----------

def obter_saldo(estoque, codigo):
    """Devolve o saldo de um item (zero se nunca movimentou)."""
    return estoque.get(codigo, 0)


def calcular_variacao(tipo, quantidade):
    """Devolve quanto o saldo muda: positivo soma, negativo subtrai."""
    if tipo not in TIPOS_MOVIMENTO.values():
        raise ValueError("tipo de movimento invalido.")
    quantidade = round(quantidade, CASAS_DECIMAIS)
    if tipo == "AJUSTE":
        if quantidade == 0:
            raise ValueError("o ajuste nao pode ser zero.")
        return quantidade
    if quantidade <= 0:
        raise ValueError("a quantidade deve ser maior que zero.")
    if tipo == "SAIDA":
        return -quantidade
    return quantidade


def calcular_novo_saldo(estoque, item, variacao):
    """Devolve o novo saldo, recusando saldo negativo (RN02)."""
    saldo = obter_saldo(estoque, item["codigo"])
    novo_saldo = round(saldo + variacao, CASAS_DECIMAIS)
    if novo_saldo < 0:
        raise ValueError(
            f"saldo insuficiente (saldo atual: {formatar_numero(saldo)} "
            f"{item['unidade']}). Operacao cancelada."
        )
    return novo_saldo


def registrar_movimento(dados, codigo, tipo, quantidade, documento):
    """Atualiza o saldo e grava o movimento no historico (RN10)."""
    item = buscar_item(dados["itens"], codigo)
    if not documento:
        raise ValueError("o documento ou motivo e obrigatorio.")
    variacao = calcular_variacao(tipo, quantidade)
    novo_saldo = calcular_novo_saldo(dados["estoque"], item, variacao)
    dados["estoque"][item["codigo"]] = novo_saldo
    dados["movimentos"].append({
        "data": data_hoje(),
        "codigo": item["codigo"],
        "tipo": tipo,
        "quantidade": variacao,
        "saldo": novo_saldo,
        "documento": documento,
    })


def filtrar_movimentos(movimentos, codigo):
    """Devolve somente os movimentos de um item."""
    return [mov for mov in movimentos if mov["codigo"] == codigo]


def abaixo_da_seguranca(estoque, item):
    """Informa se o saldo esta abaixo do estoque de seguranca."""
    saldo = obter_saldo(estoque, item["codigo"])
    return saldo < item["estoque_seguranca"]


# ---------- Telas ----------

def exibir_saldo(estoque, item):
    """Mostra o saldo de um item e o alerta, se for preciso."""
    saldo = formatar_numero(obter_saldo(estoque, item["codigo"]))
    seguranca = formatar_numero(item["estoque_seguranca"])
    unidade = item["unidade"]
    print(f"\nSaldo de {item['codigo']}: {saldo} {unidade}")
    if abaixo_da_seguranca(estoque, item):
        print(
            f"ALERTA: saldo ({saldo} {unidade}) abaixo do estoque "
            f"de seguranca ({seguranca} {unidade})."
        )


def ler_quantidade(tipo):
    """Le a quantidade; somente o ajuste aceita valor negativo."""
    if tipo == "AJUSTE":
        return ler_decimal(
            "Diferenca (ex.: 5 ou -2)", minimo=SEM_MINIMO
        )
    return ler_decimal("Quantidade")


def tela_movimentar(dados):
    """Tela de entrada, saida e ajuste de estoque."""
    estoque = dados["estoque"]
    print("\nMOVIMENTACAO DE ESTOQUE (Ctrl+C cancela)")
    item = buscar_item(dados["itens"], ler_texto("Codigo do item"))
    sigla = ler_escolha(
        "Tipo [E]ntrada [S]aida [A]juste", TIPOS_MOVIMENTO
    )
    tipo = TIPOS_MOVIMENTO[sigla]
    quantidade = ler_quantidade(tipo)
    # Avisa sobre o saldo antes de pedir o documento
    calcular_novo_saldo(
        estoque, item, calcular_variacao(tipo, quantidade)
    )
    documento = ler_texto("Documento ou motivo")
    registrar_movimento(
        dados, item["codigo"], tipo, quantidade, documento
    )
    print("\nMovimento registrado com sucesso.")
    exibir_saldo(estoque, item)


def tela_saldo(dados):
    """Tela de consulta do saldo de um item."""
    item = buscar_item(dados["itens"], ler_texto("Codigo do item"))
    print(f"\n{item['codigo']} {item['descricao']}")
    exibir_saldo(dados["estoque"], item)


def formatar_variacao(valor):
    """Mostra o sinal de mais nos valores positivos."""
    sinal = "+" if valor > 0 else ""
    return f"{sinal}{formatar_numero(valor)}"


def tela_kardex(dados):
    """Tela com o historico de movimentos de um item."""
    item = buscar_item(dados["itens"], ler_texto("Codigo do item"))
    movimentos = filtrar_movimentos(dados["movimentos"], item["codigo"])
    print(
        f"\nKARDEX - {item['codigo']} {item['descricao']} "
        f"({item['unidade']})"
    )
    if not movimentos:
        print("Nenhum movimento registrado.")
    else:
        print(
            f"{'Data':<12}{'Tipo':<9}{'Qtde':>10}{'Saldo':>10}"
            "  Documento"
        )
        print("-" * 75)
        for mov in movimentos:
            print(
                f"{mov['data']:<12}{mov['tipo']:<9}"
                f"{formatar_variacao(mov['quantidade']):>10}"
                f"{formatar_numero(mov['saldo']):>10}"
                f"  {mov['documento']}"
            )
    exibir_saldo(dados["estoque"], item)
