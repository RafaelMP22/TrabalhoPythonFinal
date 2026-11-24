"""Cadastro de itens (RF02 e RN01)."""

from utils import (
    formatar_moeda,
    formatar_numero,
    ler_decimal,
    ler_inteiro,
    ler_texto,
)

# A ordem dos tipos tambem sera usada no MRP (RN04)
TIPOS = ("PA", "SA", "MP")
UNIDADES = {"UN": "un", "M": "m", "KG": "kg", "L": "L"}
CAMPOS_NUMERICOS = ("custo", "lead_time", "estoque_seguranca", "lote_minimo")


# ---------- Logica ----------

def validar_codigo(codigo):
    """Confere o formato Tipo-Numero e devolve o codigo padronizado."""
    codigo = codigo.strip().upper()
    tipo, _, numero = codigo.partition("-")
    if tipo not in TIPOS or len(numero) != 3 or not numero.isdecimal():
        raise ValueError("codigo invalido. Use o formato PA-001.")
    return codigo


def validar_codigo_novo(itens, codigo):
    """Confere o formato e garante que o codigo ainda nao existe."""
    codigo = validar_codigo(codigo)
    if codigo in itens:
        raise ValueError(f"o item {codigo} ja esta cadastrado.")
    return codigo


def validar_campos(campos):
    """Confere os dados de um item antes de gravar."""
    if not campos["descricao"]:
        raise ValueError("a descricao e obrigatoria.")
    if campos["unidade"] not in UNIDADES.values():
        raise ValueError("unidade de medida invalida.")
    for campo in CAMPOS_NUMERICOS:
        if campos[campo] < 0:
            raise ValueError(f"o campo {campo} nao pode ser negativo.")


def buscar_item(itens, codigo):
    """Devolve o item do codigo ou avisa que ele nao existe."""
    codigo = validar_codigo(codigo)
    if codigo not in itens:
        raise ValueError(f"o item {codigo} nao esta cadastrado.")
    return itens[codigo]


def cadastrar_item(itens, codigo, campos):
    """Inclui um novo item no cadastro."""
    codigo = validar_codigo_novo(itens, codigo)
    validar_campos(campos)
    itens[codigo] = {"codigo": codigo, "tipo": codigo[:2], **campos}


def alterar_item(itens, codigo, campos):
    """Altera os dados de um item, mantendo codigo e tipo."""
    item = buscar_item(itens, codigo)
    validar_campos(campos)
    item.update(campos)


def chave_ordem(codigo):
    """Devolve a posicao do tipo e o codigo, para ordenar."""
    return TIPOS.index(codigo[:2]), codigo


def ordenar_codigos(itens):
    """Devolve os codigos na ordem PA, SA e MP."""
    return sorted(itens, key=chave_ordem)


# ---------- Telas ----------

def ler_unidade(atual=None):
    """Le uma unidade de medida valida."""
    opcoes = ", ".join(UNIDADES.values())
    while True:
        texto = ler_texto(f"Unidade ({opcoes})", atual)
        unidade = UNIDADES.get(texto.upper())
        if unidade:
            return unidade
        print("ERRO: unidade invalida.")


def ler_campos(atual=None):
    """Le os dados de um item novo ou de um item ja existente."""
    if atual is None:
        atual = {}
    return {
        "descricao": ler_texto("Descricao", atual.get("descricao")),
        "unidade": ler_unidade(atual.get("unidade")),
        "custo": ler_decimal("Custo unitario (R$)", atual.get("custo")),
        "lead_time": ler_inteiro(
            "Lead time (semanas)", atual.get("lead_time")
        ),
        "estoque_seguranca": ler_decimal(
            "Estoque de seguranca", atual.get("estoque_seguranca")
        ),
        "lote_minimo": ler_decimal(
            "Lote minimo", atual.get("lote_minimo")
        ),
    }


def tela_cadastrar(dados):
    """Tela de cadastro de um item."""
    itens = dados["itens"]
    print("\nCADASTRO DE ITEM (Ctrl+C cancela)")
    codigo = validar_codigo_novo(itens, ler_texto("Codigo (ex.: PA-001)"))
    cadastrar_item(itens, codigo, ler_campos())
    print(f"\nItem {codigo} cadastrado com sucesso.")


def tela_listar(dados):
    """Tela com a lista de itens cadastrados."""
    itens = dados["itens"]
    if not itens:
        print("\nNenhum item cadastrado.")
        return
    print("\nITENS CADASTRADOS")
    print(
        f"{'Codigo':<8}{'Descricao':<28}{'Tipo':<5}{'Un':<4}"
        f"{'Custo':>10}{'LT':>4}{'ES':>8}{'Lote':>8}"
    )
    print("-" * 75)
    for codigo in ordenar_codigos(itens):
        item = itens[codigo]
        print(
            f"{codigo:<8}{item['descricao'][:27]:<28}{item['tipo']:<5}"
            f"{item['unidade']:<4}{formatar_moeda(item['custo']):>10}"
            f"{item['lead_time']:>4}"
            f"{formatar_numero(item['estoque_seguranca']):>8}"
            f"{formatar_numero(item['lote_minimo']):>8}"
        )
    print("LT = lead time (semanas) | ES = estoque de seguranca")


def tela_alterar(dados):
    """Tela de alteracao de um item."""
    itens = dados["itens"]
    print("\nALTERACAO DE ITEM (ENTER mantem o valor, Ctrl+C cancela)")
    item = buscar_item(itens, ler_texto("Codigo do item"))
    alterar_item(itens, item["codigo"], ler_campos(item))
    print(f"\nItem {item['codigo']} alterado com sucesso.")
