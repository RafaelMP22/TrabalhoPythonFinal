"""Menus e navegacao do sistema MRP II - Pedal Forte (RF01)."""

import capacidade
import custos
import estoque
import estrutura
import graficos
import itens
import mps
import mrp
import ordens
import persistencia
import relatorios


LARGURA = 50


# Cada opcao guarda: (descricao, funcao ou submenu)
MENU_ITENS = {
    "1": ("Cadastrar item", itens.tela_cadastrar),
    "2": ("Listar itens", itens.tela_listar),
    "3": ("Alterar item", itens.tela_alterar),
}

MENU_ESTRUTURA = {
    "1": ("Cadastrar ou alterar componente", estrutura.tela_cadastrar),
    "2": ("Exibir estrutura do produto", estrutura.tela_exibir),
    "3": ("Remover componente", estrutura.tela_remover),
}

MENU_CENTROS = {
    "1": ("Cadastrar ou alterar centro", capacidade.tela_cadastrar_centro),
    "2": ("Listar centros", capacidade.tela_listar_centros),
}

MENU_ROTEIROS = {
    "1": ("Cadastrar ou alterar roteiro", capacidade.tela_cadastrar_roteiro),
    "2": ("Listar roteiros", capacidade.tela_listar_roteiros),
}

MENU_CADASTROS = {
    "1": ("Itens", MENU_ITENS),
    "2": ("Estrutura de produto (BOM)", MENU_ESTRUTURA),
    "3": ("Centros de trabalho", MENU_CENTROS),
    "4": ("Roteiros", MENU_ROTEIROS),
}

MENU_ESTOQUE = {
    "1": ("Registrar movimentacao", estoque.tela_movimentar),
    "2": ("Consultar saldo", estoque.tela_saldo),
    "3": ("Consultar kardex", estoque.tela_kardex),
}

MENU_MPS = {
    "1": ("Cadastrar ou alterar demanda", mps.tela_cadastrar),
    "2": ("Exibir plano mestre", mps.tela_exibir),
}

MENU_MRP = {
    "1": ("Executar calculo MRP", mrp.tela_executar),
    "2": ("Exibir registro de um item", mrp.tela_registro),
}

MENU_ORDENS = {
    "1": ("Listar ordens", ordens.tela_listar),
    "2": ("Firmar ordens", ordens.tela_firmar),
    "3": ("Liberar ordens", ordens.tela_liberar),
    "4": ("Apontar producao (encerra a OP)", ordens.tela_apontar),
    "5": ("Receber compra (encerra a OC)", ordens.tela_receber),
}

MENU_CUSTOS = {
    "1": ("Resumo dos itens fabricados", custos.tela_resumo),
    "2": ("Detalhar um item", custos.tela_detalhar),
}

MENU_RELATORIOS = {
    "1": ("Exportar posicao de estoque", relatorios.tela_estoque),
    "2": ("Exportar lista de ordens", relatorios.tela_ordens),
}

MENU_GRAFICOS = {
    "1": ("Posicao de estoque", graficos.tela_estoque),
    "2": ("Estoque projetado de um item", graficos.tela_projetado),
    "3": ("Ordens por semana de entrega", graficos.tela_ordens),
    "4": ("Carga x capacidade", graficos.tela_carga),
}

MENU_PRINCIPAL = {
    "1": ("Cadastros (itens, estrutura, centros, roteiros)", MENU_CADASTROS),
    "2": ("Estoque (movimentar, saldo, kardex)", MENU_ESTOQUE),
    "3": ("Plano Mestre de Producao (MPS)", MENU_MPS),
    "4": ("Executar MRP", MENU_MRP),
    "5": ("Ordens de producao e de compra", MENU_ORDENS),
    "6": ("Carga x capacidade (CRP)", capacidade.tela_carga),
    "7": ("Custo padrao dos produtos", MENU_CUSTOS),
    "8": ("Relatorios (exportar CSV)", MENU_RELATORIOS),
    "9": ("Graficos de gestao", MENU_GRAFICOS),
}


def exibir_menu(titulo, opcoes, texto_saida):
    """Mostra o titulo e as opcoes de um menu."""
    print()
    print("=" * LARGURA)
    print(titulo.center(LARGURA))
    print("=" * LARGURA)
    for tecla, (descricao, _) in opcoes.items():
        print(f"{tecla}. {descricao}")
    print(f"0. {texto_saida}")
    print("-" * LARGURA)


def ler_opcao(opcoes):
    """Pede uma opcao ate o usuario digitar uma valida."""
    while True:
        escolha = input("Escolha uma opcao: ").strip()
        if escolha == "0" or escolha in opcoes:
            return escolha
        print("ERRO: opcao invalida. Tente novamente.")


def pausar():
    """Espera o usuario antes de voltar ao menu."""
    input("\nPressione ENTER para continuar...")


def executar_acao(acao, dados):
    """Executa uma funcao, salva os dados e trata os erros."""
    try:
        acao(dados)
        persistencia.salvar_dados(dados)
    except ValueError as erro:
        print(f"\nERRO: {erro}")
    except KeyboardInterrupt:
        print("\nOperacao cancelada.")
    pausar()


def executar_menu(titulo, opcoes, dados, texto_saida="Voltar"):
    """Repete um menu ate o usuario escolher 0."""
    while True:
        exibir_menu(titulo, opcoes, texto_saida)
        escolha = ler_opcao(opcoes)
        if escolha == "0":
            return
        descricao, destino = opcoes[escolha]
        # Se o destino for um dicionario, ele e um submenu
        if isinstance(destino, dict):
            executar_menu(descricao.upper(), destino, dados)
        else:
            executar_acao(destino, dados)


def menu_principal(dados):
    """Abre o menu principal do sistema."""
    titulo = "MRP II - PEDAL FORTE BICICLETAS"
    executar_menu(titulo, MENU_PRINCIPAL, dados, "Sair")
    print("\nSistema encerrado. Ate logo!")
