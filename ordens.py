"""Ordens de producao e de compra (RF09, RF10, RF11 e RN08)."""

from estoque import CASAS_DECIMAIS, obter_saldo, registrar_movimento
from estrutura import obter_componentes
from utils import formatar_numero, ler_texto

# Para qual status cada ordem pode avancar (RF10)
PROXIMO_STATUS = {
    "PLANEJADA": "FIRME",
    "FIRME": "LIBERADA",
    "LIBERADA": "ENCERRADA",
}


# ---------- Logica ----------

def definir_tipo(codigo):
    """Devolve OC para materia-prima e OP para item fabricado."""
    return "OC" if codigo.startswith("MP") else "OP"


def gerar_numero(ordens, tipo):
    """Devolve o proximo numero livre do tipo, como OP-0010."""
    usados = [
        int(ordem["numero"].split("-")[1])
        for ordem in ordens if ordem["tipo"] == tipo
    ]
    return f"{tipo}-{max(usados, default=0) + 1:04d}"


def substituir_planejadas(dados, sugestoes):
    """Apaga as ordens planejadas e cria as novas (RN08)."""
    ordens = [
        ordem for ordem in dados["ordens"]
        if ordem["status"] != "PLANEJADA"
    ]
    novas = []
    for sugestao in sugestoes:
        tipo = definir_tipo(sugestao["codigo"])
        nova = {
            "numero": gerar_numero(ordens, tipo),
            "tipo": tipo,
            **sugestao,
            "status": "PLANEJADA",
        }
        ordens.append(nova)
        novas.append(nova)
    dados["ordens"] = ordens
    return novas


def filtrar_ordens(ordens, status, tipo=None):
    """Devolve as ordens de um status e, se informado, de um tipo."""
    return [
        ordem for ordem in ordens
        if ordem["status"] == status and tipo in (None, ordem["tipo"])
    ]


def buscar_ordem(ordens, numero):
    """Devolve a ordem do numero ou avisa que ela nao existe."""
    numero = numero.strip().upper()
    for ordem in ordens:
        if ordem["numero"] == numero:
            return ordem
    raise ValueError(f"a ordem {numero} nao existe.")


def validar_avanco(ordem, novo_status):
    """Garante que a ordem siga o ciclo, sem pular etapas."""
    if PROXIMO_STATUS.get(ordem["status"]) != novo_status:
        raise ValueError(
            f"a ordem {ordem['numero']} esta {ordem['status']} "
            f"e nao pode passar para {novo_status}."
        )


def avancar_ordens(ordens, numeros, novo_status):
    """Muda o status de uma ou mais ordens; se uma falhar, nada muda."""
    escolhidas = [buscar_ordem(ordens, numero) for numero in numeros]
    for ordem in escolhidas:
        validar_avanco(ordem, novo_status)
    for ordem in escolhidas:
        ordem["status"] = novo_status


def calcular_consumos(estrutura, ordem):
    """Devolve quanto a OP consome de cada componente."""
    componentes = obter_componentes(estrutura, ordem["codigo"])
    return {
        codigo: round(quantidade * ordem["quantidade"], CASAS_DECIMAIS)
        for codigo, quantidade in componentes.items()
    }


def listar_faltas(estoque, consumos):
    """Devolve um aviso para cada componente sem saldo suficiente."""
    faltas = []
    for codigo, consumo in consumos.items():
        saldo = obter_saldo(estoque, codigo)
        if consumo > saldo:
            faltas.append(
                f"  {codigo}: necessario {formatar_numero(consumo)}, "
                f"saldo {formatar_numero(saldo)}"
            )
    return faltas


def apontar_producao(dados, ordem):
    """Baixa os componentes, da entrada no item e encerra a OP."""
    numero, codigo = ordem["numero"], ordem["codigo"]
    if ordem["tipo"] != "OP":
        raise ValueError(f"{numero} nao e uma ordem de producao.")
    validar_avanco(ordem, "ENCERRADA")
    consumos = calcular_consumos(dados["estrutura"], ordem)
    if not consumos:
        raise ValueError(f"{codigo} nao possui estrutura cadastrada.")
    faltas = listar_faltas(dados["estoque"], consumos)
    if faltas:
        raise ValueError(
            f"falta componente para a {numero}:\n" + "\n".join(faltas)
        )
    # So movimenta o estoque depois de conferir tudo
    for componente, consumo in consumos.items():
        registrar_movimento(
            dados, componente, "SAIDA", consumo, f"{numero} ({codigo})"
        )
    registrar_movimento(
        dados, codigo, "ENTRADA", ordem["quantidade"], numero
    )
    ordem["status"] = "ENCERRADA"


def receber_compra(dados, ordem):
    """Da entrada no material comprado e encerra a OC."""
    if ordem["tipo"] != "OC":
        raise ValueError(f"{ordem['numero']} nao e uma ordem de compra.")
    validar_avanco(ordem, "ENCERRADA")
    registrar_movimento(
        dados, ordem["codigo"], "ENTRADA",
        ordem["quantidade"], ordem["numero"],
    )
    ordem["status"] = "ENCERRADA"


# ---------- Telas ----------

def descrever_status(ordem):
    """Mostra ATRASADA na ordem planejada que ja perdeu o prazo."""
    if ordem["atrasada"] and ordem["status"] == "PLANEJADA":
        return "ATRASADA"
    return ordem["status"]


def exibir_ordens(ordens):
    """Mostra uma tabela de ordens."""
    print(
        f"{'Ordem':<9}{'Tipo':<6}{'Item':<8}{'Qtde':>8}"
        f"{'Liberar':>9}{'Entregar':>10}  Status"
    )
    print("-" * 63)
    for ordem in ordens:
        liberar = f"S{ordem['semana_liberacao']}"
        entregar = f"S{ordem['semana_entrega']}"
        print(
            f"{ordem['numero']:<9}{ordem['tipo']:<6}{ordem['codigo']:<8}"
            f"{formatar_numero(ordem['quantidade']):>8}"
            f"{liberar:>9}{entregar:>10}  {descrever_status(ordem)}"
        )


def exibir_opcoes(ordens, status, tipo=None):
    """Mostra as ordens disponiveis e informa se existe alguma."""
    opcoes = filtrar_ordens(ordens, status, tipo)
    if not opcoes:
        print(f"\nNenhuma {tipo or 'ordem'} com status {status}.")
        return False
    print()
    exibir_ordens(opcoes)
    print()
    return True


def avancar_pela_tela(dados, status_atual):
    """Pede os numeros das ordens e avanca o status delas."""
    ordens = dados["ordens"]
    if not exibir_opcoes(ordens, status_atual):
        return
    novo_status = PROXIMO_STATUS[status_atual]
    numeros = ler_texto("Numero(s), separados por espaco").split()
    avancar_ordens(ordens, numeros, novo_status)
    print(f"\n{len(numeros)} ordem(ns) com status {novo_status}.")


def tela_listar(dados):
    """Tela com todas as ordens."""
    if not dados["ordens"]:
        print("\nNenhuma ordem cadastrada.")
        return
    print("\nORDENS DE PRODUCAO E DE COMPRA")
    exibir_ordens(dados["ordens"])


def tela_firmar(dados):
    """Tela para firmar ordens planejadas."""
    avancar_pela_tela(dados, "PLANEJADA")


def tela_liberar(dados):
    """Tela para liberar ordens firmes."""
    avancar_pela_tela(dados, "FIRME")


def tela_apontar(dados):
    """Tela de apontamento da producao de uma OP liberada."""
    if not exibir_opcoes(dados["ordens"], "LIBERADA", "OP"):
        return
    ordem = buscar_ordem(dados["ordens"], ler_texto("Numero da OP"))
    apontar_producao(dados, ordem)
    saldo = obter_saldo(dados["estoque"], ordem["codigo"])
    print(f"\n{ordem['numero']} apontada e encerrada.")
    print(f"Saldo de {ordem['codigo']}: {formatar_numero(saldo)}")


def tela_receber(dados):
    """Tela de recebimento de uma OC liberada."""
    if not exibir_opcoes(dados["ordens"], "LIBERADA", "OC"):
        return
    ordem = buscar_ordem(dados["ordens"], ler_texto("Numero da OC"))
    receber_compra(dados, ordem)
    saldo = obter_saldo(dados["estoque"], ordem["codigo"])
    print(f"\n{ordem['numero']} recebida e encerrada.")
    print(f"Saldo de {ordem['codigo']}: {formatar_numero(saldo)}")
