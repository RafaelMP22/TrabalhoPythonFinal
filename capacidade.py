"""Centros de trabalho, roteiros e CRP (RF06, RF12 e RN09)."""

from estoque import CASAS_DECIMAIS
from itens import buscar_item, ordenar_codigos
from mps import SEMANAS
from utils import (
    formatar_moeda,
    formatar_numero,
    ler_decimal,
    ler_texto,
)


# ---------- Logica: centros e roteiros ----------

def validar_codigo_centro(codigo):
    """Confere o formato CT-01 e devolve o codigo padronizado."""
    codigo = codigo.strip().upper()
    prefixo, _, numero = codigo.partition("-")
    if prefixo != "CT" or len(numero) != 2 or not numero.isdecimal():
        raise ValueError("codigo invalido. Use o formato CT-01.")
    return codigo


def buscar_centro(centros, codigo):
    """Devolve o centro do codigo ou avisa que ele nao existe."""
    codigo = validar_codigo_centro(codigo)
    if codigo not in centros:
        raise ValueError(f"o centro {codigo} nao esta cadastrado.")
    return centros[codigo]


def gravar_centro(centros, codigo, campos):
    """Inclui ou altera um centro de trabalho."""
    codigo = validar_codigo_centro(codigo)
    if not campos["descricao"]:
        raise ValueError("a descricao e obrigatoria.")
    if campos["capacidade"] <= 0:
        raise ValueError("a capacidade deve ser maior que zero.")
    if campos["custo_hora"] < 0:
        raise ValueError("o custo-hora nao pode ser negativo.")
    centros[codigo] = {"codigo": codigo, **campos}


def buscar_fabricado(itens, codigo):
    """Devolve um item fabricado (PA ou SA)."""
    item = buscar_item(itens, codigo)
    if item["tipo"] == "MP":
        raise ValueError(
            f"{item['codigo']} e comprado. Informe um item PA ou SA."
        )
    return item


def gravar_roteiro(dados, cod_item, cod_centro, tempo):
    """Informa o centro e o tempo por unidade de um item fabricado."""
    item = buscar_fabricado(dados["itens"], cod_item)
    centro = buscar_centro(dados["centros"], cod_centro)
    if tempo <= 0:
        raise ValueError("o tempo deve ser maior que zero.")
    dados["roteiros"][item["codigo"]] = {
        "centro": centro["codigo"],
        "tempo": tempo,
    }


# ---------- Logica: carga x capacidade ----------

def calcular_carga(dados, cod_centro):
    """Soma as horas das OPs liberadas em cada semana (RN09)."""
    cargas = [0] * SEMANAS
    for ordem in dados["ordens"]:
        roteiro = dados["roteiros"].get(ordem["codigo"])
        if not roteiro or roteiro["centro"] != cod_centro:
            continue
        semana = ordem["semana_liberacao"]
        if ordem["status"] != "ENCERRADA" and 1 <= semana <= SEMANAS:
            cargas[semana - 1] += ordem["quantidade"] * roteiro["tempo"]
    return [round(carga, CASAS_DECIMAIS) for carga in cargas]


def listar_sobrecargas(cargas, capacidade):
    """Devolve as semanas em que a carga supera a capacidade."""
    return [
        semana for semana, carga in enumerate(cargas, start=1)
        if carga > capacidade
    ]


def listar_sem_roteiro(dados):
    """Devolve os itens fabricados que ainda nao tem roteiro."""
    return [
        codigo for codigo in ordenar_codigos(dados["itens"])
        if dados["itens"][codigo]["tipo"] != "MP"
        and codigo not in dados["roteiros"]
    ]


# ---------- Telas ----------

def formatar_horas(valor):
    """Formata horas com uma casa decimal e virgula."""
    return f"{valor:.1f}".replace(".", ",")


def tela_cadastrar_centro(dados):
    """Tela de cadastro e alteracao de um centro de trabalho."""
    centros = dados["centros"]
    print("\nCENTRO DE TRABALHO (Ctrl+C cancela)")
    codigo = validar_codigo_centro(ler_texto("Codigo (ex.: CT-01)"))
    atual = centros.get(codigo, {})
    campos = {
        "descricao": ler_texto("Descricao", atual.get("descricao")),
        "capacidade": ler_decimal(
            "Capacidade (horas/semana)", atual.get("capacidade")
        ),
        "custo_hora": ler_decimal(
            "Custo-hora (R$)", atual.get("custo_hora")
        ),
    }
    gravar_centro(centros, codigo, campos)
    print(f"\nCentro {codigo} gravado com sucesso.")


def tela_listar_centros(dados):
    """Tela com os centros de trabalho."""
    centros = dados["centros"]
    if not centros:
        print("\nNenhum centro de trabalho cadastrado.")
        return
    print("\nCENTROS DE TRABALHO")
    print(
        f"{'Codigo':<8}{'Descricao':<28}"
        f"{'Horas/semana':>13}{'Custo-hora':>12}"
    )
    print("-" * 61)
    for codigo in sorted(centros):
        centro = centros[codigo]
        print(
            f"{codigo:<8}{centro['descricao'][:27]:<28}"
            f"{formatar_horas(centro['capacidade']):>13}"
            f"{formatar_moeda(centro['custo_hora']):>12}"
        )


def tela_cadastrar_roteiro(dados):
    """Tela de cadastro e alteracao do roteiro de um item."""
    print("\nROTEIRO DE FABRICACAO (Ctrl+C cancela)")
    item = buscar_fabricado(dados["itens"], ler_texto("Codigo do item"))
    codigo = item["codigo"]
    atual = dados["roteiros"].get(codigo, {})
    centro = buscar_centro(
        dados["centros"], ler_texto("Centro", atual.get("centro"))
    )
    tempo = ler_decimal("Horas por unidade", atual.get("tempo"))
    gravar_roteiro(dados, codigo, centro["codigo"], tempo)
    print(f"\nRoteiro de {codigo} gravado com sucesso.")


def tela_listar_roteiros(dados):
    """Tela com o roteiro de cada item fabricado."""
    print("\nROTEIROS")
    print(
        f"{'Item':<8}{'Descricao':<28}{'Centro':<8}{'Horas/un':>10}"
    )
    print("-" * 54)
    for codigo in ordenar_codigos(dados["roteiros"]):
        roteiro = dados["roteiros"][codigo]
        descricao = dados["itens"][codigo]["descricao"][:27]
        print(
            f"{codigo:<8}{descricao:<28}{roteiro['centro']:<8}"
            f"{formatar_numero(roteiro['tempo']):>10}"
        )
    exibir_sem_roteiro(dados)


def exibir_sem_roteiro(dados):
    """Avisa quais itens fabricados estao sem roteiro."""
    faltando = listar_sem_roteiro(dados)
    if faltando:
        print(f"\nAVISO: itens sem roteiro: {', '.join(faltando)}.")


def exibir_carga(dados, centro):
    """Mostra a carga semanal de um centro de trabalho."""
    capacidade = centro["capacidade"]
    cargas = calcular_carga(dados, centro["codigo"])
    sobrecargas = listar_sobrecargas(cargas, capacidade)
    print(
        f"\nCARGA x CAPACIDADE - {centro['codigo']} {centro['descricao']} "
        f"({formatar_horas(capacidade)} h/semana)"
    )
    print(f"{'Sem':<4}{'Carga(h)':>10}{'Uso(%)':>8}")
    for semana, carga in enumerate(cargas, start=1):
        uso = carga / capacidade * 100
        barra = "#" * round(uso / 10)
        aviso = " SOBRECARGA" if semana in sobrecargas else ""
        print(
            f"{semana:<4}{formatar_horas(carga):>10}{uso:>8.0f}"
            f"  {barra}{aviso}"
        )
    if sobrecargas:
        semanas = ", ".join(str(semana) for semana in sobrecargas)
        print(
            "Sugestao: antecipar OPs ou programar hora extra "
            f"na(s) semana(s) {semanas}."
        )


def tela_carga(dados):
    """Tela com a carga x capacidade de todos os centros (RF12)."""
    centros = dados["centros"]
    if not centros:
        print("\nNenhum centro de trabalho cadastrado.")
        return
    for codigo in sorted(centros):
        exibir_carga(dados, centros[codigo])
    exibir_sem_roteiro(dados)
