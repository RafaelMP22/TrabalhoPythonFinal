"""Estrutura de produto - BOM (RF03 e RN03)."""

from itens import buscar_item, ordenar_codigos
from utils import formatar_numero, ler_decimal, ler_texto

# Tipos de componente que cada tipo de pai aceita (RN03)
TIPOS_ACEITOS = {
    "PA": ("SA", "MP"),
    "SA": ("MP",),
    "MP": (),
}
LARGURA_LINHA = 48


# ---------- Logica ----------

def buscar_pai(itens, codigo):
    """Devolve um item que pode ter estrutura (PA ou SA)."""
    pai = buscar_item(itens, codigo)
    if not TIPOS_ACEITOS[pai["tipo"]]:
        raise ValueError(f"{pai['codigo']} e MP e nao possui estrutura.")
    return pai


def buscar_componente(itens, pai, codigo):
    """Devolve um item que pode ser componente do pai."""
    componente = buscar_item(itens, codigo)
    aceitos = TIPOS_ACEITOS[pai["tipo"]]
    if componente["tipo"] not in aceitos:
        raise ValueError(
            f"um item {pai['tipo']} so aceita: {', '.join(aceitos)}."
        )
    return componente


def obter_componentes(estrutura, codigo):
    """Devolve os componentes diretos de um item."""
    return estrutura.get(codigo, {})


def gravar_componente(itens, estrutura, cod_pai, cod_comp, quantidade):
    """Inclui um componente no pai ou altera a quantidade dele."""
    pai = buscar_pai(itens, cod_pai)
    componente = buscar_componente(itens, pai, cod_comp)
    if quantidade <= 0:
        raise ValueError("a quantidade deve ser maior que zero.")
    componentes = estrutura.setdefault(pai["codigo"], {})
    componentes[componente["codigo"]] = quantidade


def remover_componente(estrutura, cod_pai, cod_comp):
    """Retira um componente da estrutura do pai."""
    componentes = obter_componentes(estrutura, cod_pai)
    if cod_comp not in componentes:
        raise ValueError(f"{cod_comp} nao e componente de {cod_pai}.")
    del componentes[cod_comp]


def explodir(estrutura, codigo, nivel=0, quantidade=1):
    """Percorre a estrutura e devolve (nivel, codigo, quantidade)."""
    linhas = [(nivel, codigo, quantidade)]
    componentes = obter_componentes(estrutura, codigo)
    for componente in ordenar_codigos(componentes):
        linhas += explodir(
            estrutura, componente, nivel + 1, componentes[componente]
        )
    return linhas


# ---------- Telas ----------

def formatar_linha(itens, linha):
    """Monta o texto de uma linha da estrutura indentada."""
    nivel, codigo, quantidade = linha
    item = itens[codigo]
    texto = f"{'    ' * nivel}[{nivel}] {codigo} {item['descricao']} "
    if nivel == 0:
        return texto.rstrip()
    valor = f"{formatar_numero(quantidade)} {item['unidade']}"
    return f"{texto.ljust(LARGURA_LINHA, '.')} {valor}"


def tela_cadastrar(dados):
    """Tela de cadastro de um componente."""
    itens = dados["itens"]
    estrutura = dados["estrutura"]
    print("\nCADASTRO DE COMPONENTE (Ctrl+C cancela)")
    pai = buscar_pai(itens, ler_texto("Codigo do item pai"))
    componente = buscar_componente(
        itens, pai, ler_texto("Codigo do componente")
    )
    cod_pai = pai["codigo"]
    cod_comp = componente["codigo"]
    # Se o componente ja existir, mostra a quantidade atual
    atual = obter_componentes(estrutura, cod_pai).get(cod_comp)
    quantidade = ler_decimal(
        f"Quantidade por unidade ({componente['unidade']})", atual
    )
    gravar_componente(itens, estrutura, cod_pai, cod_comp, quantidade)
    print(f"\n{cod_comp} gravado na estrutura de {cod_pai}.")


def tela_exibir(dados):
    """Tela com a estrutura indentada de um produto."""
    itens = dados["itens"]
    estrutura = dados["estrutura"]
    produto = buscar_pai(itens, ler_texto("Codigo do produto"))
    codigo = produto["codigo"]
    if not obter_componentes(estrutura, codigo):
        print(f"\n{codigo} ainda nao possui componentes.")
        return
    print("\nESTRUTURA DE PRODUTO")
    for linha in explodir(estrutura, codigo):
        print(formatar_linha(itens, linha))
    print("\n[n] = nivel do item | quantidade por unidade do item pai")


def tela_remover(dados):
    """Tela para retirar um componente da estrutura."""
    itens = dados["itens"]
    print("\nREMOCAO DE COMPONENTE (Ctrl+C cancela)")
    pai = buscar_pai(itens, ler_texto("Codigo do item pai"))
    componente = buscar_item(itens, ler_texto("Codigo do componente"))
    remover_componente(
        dados["estrutura"], pai["codigo"], componente["codigo"]
    )
    print(f"\n{componente['codigo']} removido de {pai['codigo']}.")
