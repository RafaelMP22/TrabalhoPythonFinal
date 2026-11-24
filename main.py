"""Ponto de entrada do sistema MRP II - Pedal Forte."""

from menu import menu_principal
from persistencia import carregar_dados


def main():
    """Carrega os dados e abre o menu principal."""
    try:
        dados = carregar_dados()
    except ValueError as erro:
        print(f"ERRO: {erro}")
        print("Corrija o arquivo e execute o sistema novamente.")
        return
    try:
        menu_principal(dados)
    except (KeyboardInterrupt, EOFError):
        print("\n\nSistema encerrado pelo usuario.")


if __name__ == "__main__":
    main()
