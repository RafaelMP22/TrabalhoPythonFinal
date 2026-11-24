# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) para a fábrica fictícia Pedal Forte Bicicletas, desenvolvido em Python com interface em modo texto.

A cada execução, o sistema responde: o que produzir ou comprar, quanto, quando e se há capacidade para isso.

- Disciplina: Programação em Python - Engenharia de Computação
- Instituição: UFCI-MG (antigo CEFET-MG), Campus Divinópolis
- Professor: Guido Pantuza
- Aluno: Rafael Moreira de Paula
- Vídeo do sistema em funcionamento: [LINK]
- Vídeo de explicação do código: [LINK]

## Sumário

1. [Requisitos](#1-requisitos)
2. [Instalação e execução](#2-instalação-e-execução)
3. [Organização do projeto](#3-organização-do-projeto)
4. [Instruções de uso](#4-instruções-de-uso)
5. [Exemplo de um ciclo completo](#5-exemplo-de-um-ciclo-completo)
6. [Base de demonstração](#6-base-de-demonstração)
7. [Requisitos funcionais atendidos](#7-requisitos-funcionais-atendidos)
8. [Regras de negócio](#8-regras-de-negócio)
9. [Requisitos não funcionais](#9-requisitos-não-funcionais)
10. [Estruturas de dados](#10-estruturas-de-dados)
11. [Decisões de projeto](#11-decisões-de-projeto)
12. [Limitações conhecidas](#12-limitações-conhecidas)

A explicação detalhada do código, módulo por módulo, está em [docs/EXPLICACAO_DO_CODIGO.md](docs/EXPLICACAO_DO_CODIGO.md).

## 1. Requisitos

- Python 3.10 ou superior.
- matplotlib 3.6 ou superior, usado somente nos gráficos. Sem ele, o restante do sistema funciona normalmente.
- No Linux, o pacote `python3-tk`, para que as janelas dos gráficos sejam abertas. Sem ele, os gráficos ainda são salvos em PNG.

## 2. Instalação e execução

### Linux

```bash
git clone https://github.com/RafaelMP22/TrabalhoPythonFinal.git
cd TrabalhoPythonFinal
sudo apt install python3-venv python3-tk
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Windows

```bash
git clone https://github.com/RafaelMP22/TrabalhoPythonFinal.git
cd TrabalhoPythonFinal
python -m pip install -r requirements.txt
python main.py
```

Os dados são carregados automaticamente da pasta `data/` ao iniciar e salvos após cada operação.

Para restaurar a base de demonstração original depois de fazer testes:

```bash
git restore data
```

## 3. Organização do projeto

```
main.py           ponto de entrada
menu.py           menus e navegação
itens.py          cadastro de itens
estrutura.py      estrutura de produto (BOM)
estoque.py        movimentações, saldo e kardex
mps.py            plano mestre de produção
mrp.py            cálculo MRP
ordens.py         ordens de produção e de compra
capacidade.py     centros de trabalho, roteiros e CRP
custos.py         custo padrão
relatorios.py     exportação em CSV
graficos.py       gráficos de gestão
persistencia.py   leitura e gravação dos arquivos
utils.py          validações e formatação
requirements.txt  bibliotecas necessárias
data/             dados do sistema
docs/             documentação, relatórios e gráficos gerados
```

Os módulos de negócio são divididos em duas partes:

- Lógica: recebe parâmetros, calcula e devolve o resultado. Não usa `input` nem `print`. Quando uma regra é violada, lança `ValueError`.
- Telas: funções cujo nome começa com `tela_`. Conversam com o usuário e chamam a lógica.

As importações seguem um único sentido, o que evita importação circular:

| Nível | Módulos |
|---|---|
| 7 | `main` |
| 6 | `menu` |
| 5 | `relatorios`, `graficos` |
| 4 | `mrp`, `custos` |
| 3 | `ordens`, `capacidade` |
| 2 | `estrutura`, `estoque`, `mps` |
| 1 | `itens` |
| 0 | `utils`, `persistencia` |

Cada módulo importa apenas módulos de níveis inferiores ao seu.

## 4. Instruções de uso

Digite o número da opção e pressione ENTER. A opção 0 volta ao menu anterior ou encerra o sistema. Dentro de uma tela, `Ctrl+C` cancela a operação. Nas alterações, o valor atual aparece entre colchetes, e pressionar ENTER o mantém.

| Menu | Opções |
|---|---|
| 1. Cadastros | Itens (cadastrar, listar, alterar); estrutura (cadastrar ou alterar, exibir, remover componente); centros de trabalho; roteiros |
| 2. Estoque | Registrar movimentação, consultar saldo, consultar kardex |
| 3. Plano Mestre (MPS) | Cadastrar ou alterar a demanda, exibir o plano |
| 4. Executar MRP | Executar o cálculo e gerar as ordens, exibir o registro de um item |
| 5. Ordens | Listar, firmar, liberar, apontar produção, receber compra |
| 6. Carga x capacidade | Exibe a carga de todos os centros |
| 7. Custo padrão | Resumo dos itens fabricados, detalhamento de um item |
| 8. Relatórios | Exportar posição de estoque e lista de ordens em CSV |
| 9. Gráficos | Posição de estoque, estoque projetado, ordens por semana, carga x capacidade |

Observações:

- Os códigos dos itens seguem o formato Tipo-Número, com três dígitos: `PA-001`, `SA-020`, `MP-201`.
- Os códigos dos centros têm dois dígitos: `CT-01`.
- Números decimais aceitam vírgula ou ponto (`0,5` ou `0.5`). Não use separador de milhar.
- Firmar e liberar aceitam várias ordens de uma vez, separadas por espaço.
- Ao exibir um gráfico, o sistema aguarda o fechamento da janela.

## 5. Exemplo de um ciclo completo

Com a base de demonstração original:

1. Menu 3, opção 2: consultar o plano mestre.
2. Menu 4, opção 1: executar o MRP. São geradas as ordens planejadas, com duas mensagens de exceção.
3. Menu 4, opção 2, item `SA-020`: ver o registro MRP.
4. Menu 6: verificar a carga dos centros. O `CT-03` fica sobrecarregado nas semanas 3 e 6.
5. Menu 5, opção 4, ordem `OP-0009`: apontar a produção de 50 rodas, que já estava liberada. O saldo de `SA-020` passa de 40 para 90.
6. Menu 5, opção 2, ordens `OP-0010 OC-0003`: firmar.
7. Menu 5, opção 3, ordens `OP-0010 OC-0003`: liberar.
8. Menu 5, opção 4, ordem `OP-0010`: apontar 10 bicicletas. O saldo de `PA-001` passa a 10.
9. Menu 5, opção 5, ordem `OC-0003`: receber a compra de tinta. O saldo de `MP-101` passa de 40 para 60.
10. Menu 2, opção 3, item `SA-020`: conferir no kardex a entrada de 50 e a saída de 20.

## 6. Base de demonstração

| Conteúdo | Quantidade |
|---|---|
| Produtos acabados | 2 |
| Semiacabados | 4 |
| Matérias-primas | 10 |
| Centros de trabalho | 4 |

Os dados de `PA-001` e de sua estrutura foram montados para reproduzir os exemplos de tela do enunciado: registro MRP de `SA-020` (6.4), carga do `CT-03` (6.6) e custo padrão de R$ 792,60 (6.7). Os valores que o enunciado não informa, como os custos das matérias-primas do quadro e da roda, e os dados de `PA-002` foram definidos para a demonstração.

## 7. Requisitos funcionais atendidos

| Código | Requisito | Módulo | Onde acessar |
|---|---|---|---|
| RF01 | Menu principal | `menu.py` | Tela inicial |
| RF02 | Cadastrar, listar e alterar itens | `itens.py` | 1 > 1 |
| RF03 | Estrutura de produto em até 3 níveis | `estrutura.py` | 1 > 2 |
| RF04 | Movimentações de estoque | `estoque.py` | 2 > 1 |
| RF05 | Saldo, kardex e alerta de segurança | `estoque.py` | 2 > 2 e 2 > 3 |
| RF06 | Centros de trabalho e roteiros | `capacidade.py` | 1 > 3 e 1 > 4 |
| RF07 | Plano mestre de 8 semanas | `mps.py` | 3 |
| RF08 | Cálculo MRP e registro por item | `mrp.py` | 4 |
| RF09 | Geração de ordens planejadas | `ordens.py`, `mrp.py` | 4 > 1 |
| RF10 | Firmar, liberar e encerrar ordens | `ordens.py` | 5 |
| RF11 | Apontamento da produção | `ordens.py` | 5 > 4 |
| RF12 | Carga x capacidade (CRP) | `capacidade.py` | 6 |
| RF13 | Custo padrão | `custos.py` | 7 |
| RF14 | Exportação em CSV | `relatorios.py` | 8 |
| RF15 | Persistência na pasta `data/` | `persistencia.py` | Automático |
| RF16 | Gráficos com matplotlib | `graficos.py` | 9 |

## 8. Regras de negócio

| Código | Regra | Função que a implementa |
|---|---|---|
| RN01 | Código único no formato Tipo-Número | `itens.validar_codigo` e `itens.validar_codigo_novo` |
| RN02 | Saldo nunca negativo | `estoque.calcular_novo_saldo` |
| RN03 | Componentes permitidos por tipo | `estrutura.TIPOS_ACEITOS` e `estrutura.buscar_componente` |
| RN04 | Ordem PA, SA, MP e necessidade bruta | `mrp.calcular_mrp` e `mrp.somar_necessidade` |
| RN05 | Necessidade líquida | `mrp.calcular_registro` |
| RN06 | Lote mínimo | `mrp.calcular_lote` |
| RN07 | Lead time e ordens atrasadas | `mrp.calcular_liberacoes`, `mrp.listar_sugestoes` e `mrp.exibir_excecoes` |
| RN08 | Recebimentos programados e recálculo | `mrp.somar_programados` e `ordens.substituir_planejadas` |
| RN09 | Carga do centro e sobrecarga | `capacidade.calcular_carga` e `capacidade.listar_sobrecargas` |
| RN10 | Histórico de movimentos | `estoque.registrar_movimento` |

## 9. Requisitos não funcionais

| Código | Como foi atendido |
|---|---|
| RNF01 | Projeto individual. |
| RNF02 | Código escrito para Python 3.10 ou superior. |
| RNF03 | Nomes, espaçamento, docstrings e limite de 79 colunas conforme a PEP 8. |
| RNF04 | 14 módulos, cada um com uma responsabilidade. |
| RNF05 | Entradas validadas em `utils.py`; erros tratados em `menu.executar_acao` e em `main.main`. |
| RNF06 | Validado em: [PREENCHER: distribuição Linux e versão do Python]. |
| RNF07 | Sete arquivos JSON e um CSV. |
| RNF08 | MRP, CRP, custos e estoques implementados sem bibliotecas prontas. |
| RNF09 | Base com 2 PA, 4 SA, 10 MP e 4 centros. |
| RNF10 | Interface em modo texto. |
| RNF11 | Interface gráfica opcional, não implementada. |

## 10. Estruturas de dados

Todos os dados ficam em um único dicionário, `dados`, criado ao iniciar e passado como parâmetro entre as funções. Não há variáveis globais que mudam durante a execução.

| Chave | Tipo | Conteúdo | Arquivo |
|---|---|---|---|
| `itens` | dicionário | código -> dados do item | `itens.json` |
| `estrutura` | dicionário | pai -> {componente: quantidade} | `estrutura.json` |
| `estoque` | dicionário | código -> saldo | `estoque.json` |
| `movimentos` | lista | histórico, em ordem de registro | `movimentos.csv` |
| `centros` | dicionário | código -> dados do centro | `centros.json` |
| `roteiros` | dicionário | item -> centro e tempo | `roteiros.json` |
| `mps` | dicionário | produto -> lista de 8 demandas | `mps.json` |
| `ordens` | lista | ordens de produção e de compra | `ordens.json` |

Usei dicionários quando é preciso encontrar um registro pelo código, pois a busca é direta e a chave não se repete. Usei listas quando a ordem dos registros importa.

## 11. Decisões de projeto

Cadastros e estoque

- O código tem sempre três dígitos. Sem isso, `PA-1` e `PA-001` seriam itens diferentes.
- O tipo do item é obtido do código, e por isso os dois nunca se contradizem. Código e tipo não podem ser alterados.
- O custo digitado em PA e SA é ignorado, porque o custo deles é calculado pelo RF13.
- A quantidade na estrutura é por unidade do item pai.
- A data dos movimentos é a do dia, registrada automaticamente.
- O ajuste é informado pela diferença (por exemplo, `-2`), e não pelo saldo contado.
- Somente `registrar_movimento` altera o saldo. Assim, não existe saldo sem histórico.

MRP e ordens

- As semanas vão de 1 a 8, a partir do planejamento atual.
- O registro MRP não é gravado: é recalculado a cada consulta, com os dados atuais.
- Conforme a RN04, só as liberações planejadas geram necessidade nos componentes. OPs firmes ou liberadas não geram.
- Uma liberação anterior à semana 1 fica fora do quadro e não gera necessidade nos componentes, como no exemplo 6.4 do enunciado. Ela aparece como mensagem de exceção.
- ATRASADA é uma marca da ordem, e não um status do ciclo. A ordem segue o ciclo normal do RF10.
- A OP é encerrada ao apontar a produção, e a OC, ao receber o material. Nos dois casos, o estoque é atualizado.
- O apontamento confere todos os componentes antes de movimentar o estoque. Se faltar um, nada é alterado.
- Os números das ordens planejadas podem mudar a cada execução do MRP. A partir de FIRME, são definitivos.

Capacidade e custos

- Na RN09, "OPs liberadas naquela semana" foi interpretado como a semana de liberação da ordem, o que reproduz o exemplo 6.6.
- OPs encerradas não contam na carga, e as atrasadas ficam fora do quadro.
- O custo é arredondado para centavos em cada linha, para que a soma da tabela coincida com o total.
- O sistema avisa quando um item está sem roteiro, sem estrutura ou sem custo, pois o resultado ficaria incompleto.

Arquivos, relatórios e gráficos

- Os dados são salvos automaticamente após cada operação concluída.
- Cada arquivo de dados é gravado primeiro em um temporário e só depois substitui o anterior.
- Um arquivo corrompido não é sobrescrito: o sistema informa qual é e encerra.
- Os CSV usam ponto e vírgula e vírgula decimal, padrão das planilhas em português.
- O gráfico de estoque usa escala logarítmica, porque os saldos são muito diferentes entre si, e mostra o valor do saldo em cada barra.
- O gráfico de ordens conta ordens, e não quantidades, porque as unidades de medida são diferentes.
- O menu de gráficos não aparece no exemplo 6.1 do enunciado e foi incluído como opção 9 para atender ao RF16.

## 12. Limitações conhecidas

- Se uma OP for firmada e o MRP for executado novamente, a compra planejada dos componentes dela pode deixar de ser sugerida (consequência da RN04). A orientação é firmar a OP e as OCs correspondentes antes de recalcular.
- A carga das OPs atrasadas não é somada à semana 1.
- Não há cancelamento de ordens firmes ou liberadas.
- Cada item tem uma única operação em seu roteiro, conforme o RF06.
- O sistema é para um usuário por vez.