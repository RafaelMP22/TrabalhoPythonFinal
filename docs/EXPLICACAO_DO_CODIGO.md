# Explicação do código

Este documento explica o sistema módulo por módulo. As instruções de instalação e uso estão no [README](../README.md).

## Sumário

1. [Visão geral](#2-visão-geral)
2. [Estruturas de dados](#3-estruturas-de-dados)
3. [main.py](#4-mainpy)
4. [menu.py](#5-menupy)
5. [itens.py](#6-itenspy)
6. [estrutura.py](#7-estruturapy)
7. [estoque.py](#8-estoquepy)
8. [mps.py](#9-mpspy)
9. [mrp.py](#10-mrppy)
10. [ordens.py](#11-ordenspy)
11. [capacidade.py](#12-capacidadepy)
12. [custos.py](#13-custospy)
13. [relatorios.py](#14-relatoriospy)
14. [graficos.py](#15-graficospy)
15. [persistencia.py](#16-persistenciapy)
16. [utils.py](#17-utilspy)
17. [Recursos de Python usados](#18-recursos-de-python-usados)
18. [Ajustes que podem ser pedidos](#19-ajustes-que-podem-ser-pedidos)
19. [Perguntas e respostas](#20-perguntas-e-respostas)


## 1. Visão geral

### O caminho de uma execução

```
main.py
  1. carrega os arquivos da pasta data (persistencia.py)
  2. abre o menu principal (menu.py)
       3. o usuário escolhe uma opção
       4. o menu chama uma função tela_ de um módulo
       5. a tela lê os dados e chama a lógica do módulo
       6. a lógica calcula ou lança ValueError
       7. o menu salva os dados ou mostra o erro
       8. volta ao passo 3
```

### Lógica e tela separadas

Cada módulo de negócio tem duas partes:

- Lógica: funções que recebem parâmetros e devolvem resultados. Não usam `input` nem `print`.
- Telas: funções que conversam com o usuário.

Vantagens: a lógica pode ser testada sem digitar nada, pode ser usada por outros módulos e poderia ser aproveitada por uma interface gráfica.

### Como os erros funcionam

Quando uma regra é violada, a lógica executa `raise ValueError("mensagem")`. O erro sobe pelas funções até `executar_acao`, no `menu.py`, que mostra a mensagem e volta ao menu. Por isso as telas não precisam tratar cada erro.

```
calcular_novo_saldo   lança ValueError("saldo insuficiente ...")
registrar_movimento   não trata, o erro sobe
tela_movimentar       não trata, o erro sobe
executar_acao         except ValueError: mostra "ERRO: saldo insuficiente ..."
```

### Sentido das importações

| Nível | Módulos | Importam |
|---|---|---|
| 7 | `main` | `menu`, `persistencia` |
| 6 | `menu` | todos os módulos com telas e `persistencia` |
| 5 | `relatorios`, `graficos` | níveis abaixo |
| 4 | `mrp`, `custos` | níveis abaixo |
| 3 | `ordens`, `capacidade` | níveis abaixo |
| 2 | `estrutura`, `estoque`, `mps` | `itens`, `utils` |
| 1 | `itens` | `utils` |
| 0 | `utils`, `persistencia` | nenhum módulo do projeto |

Um módulo só importa os de nível menor. Se dois módulos se importassem mutuamente, haveria importação circular, que causa erro.

## 2. Estruturas de dados

Todo o sistema usa um único dicionário, `dados`, passado como parâmetro:

```python
dados = {
    "itens": {...},
    "estrutura": {...},
    "estoque": {...},
    "movimentos": [...],
    "centros": {...},
    "roteiros": {...},
    "mps": {...},
    "ordens": [...],
}
```

### itens

Dicionário de dicionários. A chave é o código, que não se repete.

```python
"MP-202": {
    "codigo": "MP-202", "tipo": "MP",
    "descricao": "Pneu 29 x 2.20", "unidade": "un",
    "custo": 46, "lead_time": 1,
    "estoque_seguranca": 20, "lote_minimo": 60,
}
```

### estrutura

Cada pai aponta para seus componentes diretos e as quantidades por unidade.

```python
"PA-001": {"SA-010": 1, "SA-020": 2, "MP-300": 1, "MP-301": 1},
"SA-020": {"MP-200": 1, "MP-201": 36, "MP-202": 1},
```

Os raios não aparecem em `PA-001`: eles estão na roda, e a roda está na bicicleta. Se a receita da roda mudar, basta alterar em um lugar.

### estoque e movimentos

```python
"estoque": {"MP-202": 18}

"movimentos": [
    {"data": "23/11/2026", "codigo": "MP-202", "tipo": "SAIDA",
     "quantidade": -40, "saldo": 20, "documento": "OP-0003 (SA-020)"},
]
```

O saldo é um dicionário, para consulta imediata. O histórico é uma lista, porque a ordem dos registros importa e só se acrescenta no fim.

### mps

Cada produto aponta para uma lista de 8 números. A semana 1 está na posição 0.

```python
"PA-001": [10, 30, 0, 40, 25, 0, 35, 30]
```

### centros e roteiros

```python
"centros": {"CT-03": {"codigo": "CT-03", "descricao": "Montagem final",
                      "capacidade": 16, "custo_hora": 40}}
"roteiros": {"PA-001": {"centro": "CT-03", "tempo": 0.5}}
```

O roteiro guarda somente o código do centro. Se a capacidade ou o custo-hora mudar, tudo o que usa o centro acompanha.

### ordens

```python
{"numero": "OP-0010", "tipo": "OP", "codigo": "PA-001",
 "quantidade": 10, "semana_liberacao": 0, "semana_entrega": 1,
 "atrasada": True, "status": "PLANEJADA"}
```

## 3. main.py

Papel: ponto de entrada do sistema.

Importa: `menu`, `persistencia`.

Funções:

- `main()`: carrega os dados e abre o menu principal.

Pontos importantes:

- Há dois blocos `try`. O primeiro protege só a leitura dos arquivos; o segundo, o uso do sistema. Com um só, um erro do menu poderia aparecer como se fosse um arquivo corrompido.
- Se um arquivo estiver corrompido, o sistema avisa e encerra. Começar com dados vazios apagaria o arquivo no salvamento seguinte.
- `KeyboardInterrupt` é o `Ctrl+C`. `EOFError` ocorre quando a entrada termina (`Ctrl+D` no Linux).
- `if __name__ == "__main__":` faz `main()` rodar apenas quando o arquivo é executado diretamente, e não quando é importado.

Em resumo, para o vídeo: o `main.py` é pequeno porque só liga as partes. Cada responsabilidade está em seu módulo.

## 4. menu.py

Papel: navegação. Requisito: RF01.

Importa: todos os módulos com telas e `persistencia`.

Constantes:

- `LARGURA`: largura das linhas do menu.
- `MENU_ITENS`, `MENU_ESTRUTURA`, `MENU_CENTROS`, `MENU_ROTEIROS`, `MENU_CADASTROS`, `MENU_ESTOQUE`, `MENU_MPS`, `MENU_MRP`, `MENU_ORDENS`, `MENU_CUSTOS`, `MENU_RELATORIOS`, `MENU_GRAFICOS` e `MENU_PRINCIPAL`: os menus, em forma de dicionários.

Cada menu associa uma tecla a uma tupla com a descrição e o destino:

```python
MENU_ITENS = {
    "1": ("Cadastrar item", itens.tela_cadastrar),
    "2": ("Listar itens", itens.tela_listar),
    "3": ("Alterar item", itens.tela_alterar),
}
```

A função está sem parênteses: ela é guardada, e não executada. O destino também pode ser outro dicionário, o que forma uma árvore de menus. Os menus menores são definidos antes porque o Python lê o arquivo de cima para baixo.

Funções:

- `exibir_menu(titulo, opcoes, texto_saida)`: mostra o título e as opções.
- `ler_opcao(opcoes)`: repete a pergunta até receber uma opção que exista no dicionário. Como não converte para número, digitar letras não causa erro.
- `pausar()`: espera o ENTER, para dar tempo de ler o resultado.
- `executar_acao(acao, dados)`: executa a função escolhida, salva os dados e trata os erros.
- `executar_menu(titulo, opcoes, dados, texto_saida)`: repete o menu até o usuário escolher 0.
- `menu_principal(dados)`: abre o menu principal.

Trecho principal:

```python
descricao, destino = opcoes[escolha]
if isinstance(destino, dict):
    executar_menu(descricao.upper(), destino, dados)
else:
    executar_acao(destino, dados)
```

Se o destino é um dicionário, é um submenu, e a função chama a si mesma (recursão). Se não, é uma função, que é executada. Ao digitar 0, a chamada atual termina e a anterior continua, e é assim que o "Voltar" funciona.

Em `executar_acao`, o salvamento vem depois da ação. Se ela for recusada ou cancelada, nada é salvo:

```python
try:
    acao(dados)
    persistencia.salvar_dados(dados)
except ValueError as erro:
    print(f"\nERRO: {erro}")
except KeyboardInterrupt:
    print("\nOperacao cancelada.")
```

Em resumo, para o vídeo: os menus são dados, não código repetido. Para incluir uma opção, basta acrescentar uma linha no dicionário. Todo erro e todo salvamento passam por uma única função.

## 5. itens.py

Papel: cadastro de itens. Requisitos: RF02 e RN01.

Importa: `utils`.

Constantes:

- `TIPOS`: tupla `("PA", "SA", "MP")`. A ordem é a mesma em que o MRP processa os itens.
- `UNIDADES`: dicionário que padroniza a unidade. Digitar `l` ou `L` grava sempre `L`.
- `CAMPOS_NUMERICOS`: campos que não podem ser negativos.

Lógica:

- `validar_codigo(codigo)`: padroniza e confere o formato. Com `partition("-")`, divide `"MP-202"` em `("MP", "-", "202")`. Recusa se o tipo não existir ou se o número não tiver exatamente três dígitos.
- `validar_codigo_novo(itens, codigo)`: além do formato, garante que o código ainda não existe.
- `validar_campos(campos)`: confere descrição, unidade e valores numéricos.
- `buscar_item(itens, codigo)`: devolve o item ou lança erro se não existir. É usada por vários módulos.
- `cadastrar_item(itens, codigo, campos)`: grava um item novo. O tipo é obtido dos dois primeiros caracteres do código, com `codigo[:2]`.
- `alterar_item(itens, codigo, campos)`: altera os campos com `update`. Código e tipo não mudam, porque outros dados se referem ao item por eles.
- `chave_ordem(codigo)`: devolve a posição do tipo e o código, por exemplo `(1, "SA-020")`.
- `ordenar_codigos(itens)`: ordena na sequência PA, SA, MP, usando `chave_ordem` como critério. Em ordem alfabética, MP viria antes.

Telas:

- `ler_unidade(atual)`: repete até receber uma unidade válida.
- `ler_campos(atual)`: lê todos os campos. Serve para cadastrar (sem valor atual) e alterar (mostrando o valor atual).
- `tela_cadastrar(dados)`: valida o código antes de perguntar o resto.
- `tela_listar(dados)`: mostra a tabela de itens.
- `tela_alterar(dados)`: altera um item. Como tudo é lido antes de gravar, cancelar no meio não altera nada.

Em resumo, para o vídeo: as telas já impedem valores inválidos, mas a lógica valida de novo. A tela dá conforto ao usuário, e a lógica dá garantia aos dados.

## 6. estrutura.py

Papel: estrutura de produto (BOM), a "receita" de cada item fabricado. Requisitos: RF03 e RN03.

Importa: `itens`, `utils`.

Constantes:

- `TIPOS_ACEITOS`: a RN03 em forma de dados.
- `LARGURA_LINHA`: largura usada para alinhar as quantidades.

```python
TIPOS_ACEITOS = {
    "PA": ("SA", "MP"),
    "SA": ("MP",),
    "MP": (),
}
```

A vírgula em `("MP",)` é necessária: sem ela, seria apenas um texto entre parênteses. Como o componente é sempre de um tipo abaixo do pai, não há como formar ciclos nem passar de três níveis.

Lógica:

- `buscar_pai(itens, codigo)`: devolve um item que pode ter estrutura. Recusa MP.
- `buscar_componente(itens, pai, codigo)`: devolve um item que pode ser componente do pai.
- `obter_componentes(estrutura, codigo)`: devolve os componentes diretos, ou um dicionário vazio.
- `gravar_componente(itens, estrutura, cod_pai, cod_comp, quantidade)`: inclui ou altera um componente. Usa `setdefault`, que cria a chave se ela não existir.
- `remover_componente(estrutura, cod_pai, cod_comp)`: retira um componente. Não é exigida no enunciado, mas permite corrigir erros.
- `explodir(estrutura, codigo, nivel, quantidade)`: percorre toda a estrutura.

Trecho principal:

```python
def explodir(estrutura, codigo, nivel=0, quantidade=1):
    linhas = [(nivel, codigo, quantidade)]
    componentes = obter_componentes(estrutura, codigo)
    for componente in ordenar_codigos(componentes):
        linhas += explodir(
            estrutura, componente, nivel + 1, componentes[componente]
        )
    return linhas
```

A função começa com o próprio item e chama a si mesma para cada componente, somando 1 ao nível. A recursão para na MP, que não tem componentes: o `for` não executa nenhuma vez.

```
explodir("SA-020", nível 0)
  começa com [(0, "SA-020", 1)]
  explodir("MP-200", nível 1) devolve [(1, "MP-200", 1)]
  explodir("MP-201", nível 1) devolve [(1, "MP-201", 36)]
  explodir("MP-202", nível 1) devolve [(1, "MP-202", 1)]
```

Telas:

- `formatar_linha(itens, linha)`: monta uma linha indentada, com 4 espaços por nível e o nível entre colchetes.
- `tela_cadastrar(dados)`: inclui um componente ou altera a quantidade. Se ele já existir, mostra a quantidade atual.
- `tela_exibir(dados)`: mostra a estrutura indentada.
- `tela_remover(dados)`: retira um componente.

Em resumo, para o vídeo: a regra de quem pode conter quem é uma tabela, e a exibição usa recursão. A função recursiva devolve dados, e a tela decide como mostrar.

## 7. estoque.py

Papel: movimentações, saldo e kardex. Requisitos: RF04, RF05, RN02 e RN10.

Importa: `itens`, `utils`.

Constantes:

- `TIPOS_MOVIMENTO`: traduz a letra digitada no nome do movimento.
- `CASAS_DECIMAIS`: precisão dos saldos (3 casas).
- `SEM_MINIMO`: menos infinito, usado para aceitar valores negativos no ajuste.

Lógica:

- `obter_saldo(estoque, codigo)`: devolve o saldo, ou zero se o item nunca foi movimentado.
- `calcular_variacao(tipo, quantidade)`: transforma o movimento em um número com sinal. Entrada soma, saída subtrai e ajuste aceita os dois sinais.
- `calcular_novo_saldo(estoque, item, variacao)`: calcula o novo saldo e recusa se ficar negativo (RN02). Só calcula, não grava.
- `registrar_movimento(dados, codigo, tipo, quantidade, documento)`: atualiza o saldo e acrescenta o movimento ao histórico.
- `filtrar_movimentos(movimentos, codigo)`: devolve os movimentos de um item.
- `abaixo_da_seguranca(estoque, item)`: informa se o saldo está abaixo do estoque de segurança.

A ordem dentro de `registrar_movimento` é proposital:

```
1. busca o item (erro se não existir)
2. confere o documento
3. calcula a variação e o novo saldo (erro se ficar negativo)
4. só então grava o saldo e o histórico
```

Se algo falhar antes do passo 4, nada é alterado. A RN10 é garantida porque não existe função para editar ou apagar movimentos: só se acrescenta à lista. Correções são feitas com um ajuste.

O arredondamento é necessário porque o computador guarda decimais de forma aproximada. Em Python, `0.1 + 0.2` resulta em `0.30000000000000004`.

Telas:

- `exibir_saldo(estoque, item)`: mostra o saldo e o alerta. É usada por três telas.
- `ler_quantidade(tipo)`: no ajuste, aceita valor negativo.
- `tela_movimentar(dados)`: verifica o saldo antes de pedir o documento.
- `tela_saldo(dados)`: consulta o saldo.
- `formatar_variacao(valor)`: mostra o sinal de mais nos valores positivos.
- `tela_kardex(dados)`: mostra o histórico do item.

Em resumo, para o vídeo: `registrar_movimento` é a única porta de alteração do saldo. Até o saldo inicial e o apontamento de produção passam por ela. Por isso, o saldo sempre corresponde ao histórico.

## 8. mps.py

Papel: plano mestre de produção. Requisito: RF07.

Importa: `itens`, `utils`.

Constantes:

- `SEMANAS`: horizonte de 8 semanas. Os outros módulos importam esta constante.
- `LARGURA_COLUNA`: largura das colunas da tabela.

Lógica:

- `buscar_produto(itens, codigo)`: devolve um item, desde que seja PA. A necessidade de SA e MP é calculada, nunca digitada.
- `listar_produtos(itens)`: devolve os códigos dos produtos acabados.
- `obter_demanda(mps, codigo)`: devolve a lista de 8 valores, ou 8 zeros se não houver demanda. Consultar não grava nada.
- `gravar_demanda(itens, mps, codigo, demanda)`: confere se há 8 valores e se o menor deles não é negativo. Grava uma cópia, com `list(demanda)`, para que a lista original não altere o plano depois.

Telas:

- `ler_demanda(atual)`: pergunta a demanda de cada semana. `enumerate(atual, start=1)` entrega o número da semana e o valor juntos.
- `exibir_tabela(dados, codigos)`: mostra a demanda de um ou de vários produtos.
- `tela_cadastrar(dados)`: cadastra ou altera a demanda.
- `tela_exibir(dados)`: mostra o plano de todos os produtos.

Em resumo, para o vídeo: o MPS é o ponto de partida. Ele diz quantas bicicletas entregar por semana, e o MRP calcula o resto.

## 9. mrp.py

Papel: cálculo MRP. Requisitos: RF08, RF09 e RN04 a RN08.

Importa: `estoque`, `estrutura`, `itens`, `mps`, `ordens`, `utils`.

Constantes:

- `STATUS_PROGRAMADOS`: status que contam como recebimento programado (RN08).
- `LARGURA_COLUNA`: largura das colunas do registro.
- `LINHAS_REGISTRO`: liga o texto de cada linha da tela à chave do registro.

### O que significa cada linha do registro

| Linha | Pergunta que responde |
|---|---|
| Necessidade bruta (NB) | Quanto será consumido? |
| Recebimentos programados (RP) | O que já está a caminho? |
| Estoque projetado (EP) | Quanto sobra no fim da semana? |
| Necessidade líquida (NL) | Quanto falta? |
| Recebimentos planejados | Quanto pedir, respeitando o lote mínimo? |
| Liberação planejada | Quando começar? |

### Exemplo completo: SA-020

Saldo 40, estoque de segurança 10, lote mínimo 80, lead time 1, e 50 unidades programadas para a semana 1.

| Semana | NB | Disponível (EP anterior + RP) | NL = NB + 10 - disponível | Receber | EP final |
|---|---|---|---|---|---|
| 1 | 60 | 40 + 50 = 90 | -20, portanto 0 | 0 | 30 |
| 2 | 0 | 30 | -20, portanto 0 | 0 | 30 |
| 3 | 80 | 30 | 60 | 80 | 30 |
| 4 | 50 | 30 | 30 | 80 | 60 |
| 5 | 0 | 60 | -50, portanto 0 | 0 | 60 |
| 6 | 70 | 60 | 20 | 80 | 70 |
| 7 | 60 | 70 | 0 | 0 | 10 |
| 8 | 0 | 10 | 0 | 0 | 10 |

Como o lead time é 1, o que chega nas semanas 3, 4 e 6 precisa ser liberado nas semanas 2, 3 e 5. O resultado é igual ao do exemplo 6.4 do enunciado.

Lógica:

- `arredondar(valor)`: evita que uma sobra como 0,00000001 seja tratada como necessidade e gere um lote inteiro.
- `somar_programados(ordens, codigo)`: soma, por semana de entrega, as ordens firmes e liberadas do item (RN08).
- `calcular_lote(liquida, lote_minimo)`: devolve o maior valor entre a necessidade e o lote, ou zero se não houver necessidade (RN06).
- `calcular_liberacoes(planejados, lead_time)`: recua os recebimentos pelo lead time (RN07).
- `calcular_registro(item, brutas, programados, saldo)`: calcula as seis linhas de um item (RN05).
- `somar_necessidade(brutas, liberacoes, quantidade)`: soma no componente a necessidade gerada por um pai (RN04).
- `iniciar_brutas(dados)`: começa com a demanda do MPS nos PA e zeros nos demais. Usa cópias, para não alterar o MPS.
- `calcular_mrp(dados)`: calcula todos os itens, na ordem PA, SA, MP. Lê os dados e devolve o resultado, sem alterar nada.
- `listar_sugestoes(itens, registros)`: transforma cada recebimento planejado em uma sugestão de ordem e marca as atrasadas.

Trecho principal de `calcular_registro`:

```python
anterior = saldo
for bruta, programado in zip(brutas, programados):
    disponivel = anterior + programado
    falta = bruta + item["estoque_seguranca"] - disponivel
    liquida = max(0, arredondar(falta))
    planejado = calcular_lote(liquida, item["lote_minimo"])
    anterior = arredondar(disponivel + planejado - bruta)
```

A variável `anterior` carrega o estoque projetado de uma semana para a próxima. `zip` percorre as duas listas juntas.

Trecho principal de `calcular_mrp`:

```python
for codigo in ordenar_codigos(dados["itens"]):
    registro = calcular_registro(...)
    registros[codigo] = registro
    componentes = obter_componentes(dados["estrutura"], codigo)
    for componente, quantidade in componentes.items():
        somar_necessidade(
            brutas[componente], registro["liberacao"], quantidade
        )
```

Cada item é calculado e, em seguida, empurra suas liberações para os componentes. Quando chega a vez de um item, todos os seus pais já passaram, e a necessidade dele está completa. Exemplo na semana 3 para o raio `MP-201`, que tem dois pais:

```
SA-020 libera 80 rodas x 36 raios = 2880
SA-021 libera 40 rodas x 32 raios = 1280
necessidade bruta da semana 3     = 4160
```

Cuidado tratado em `calcular_liberacoes`: em Python, uma posição negativa não dá erro. `lista[-1]` é o último elemento, e uma liberação da semana 0 iria para a semana 8. Por isso existe a verificação `if destino >= 0`.

Telas:

- `exibir_excecoes(ordens)`: mostra uma mensagem para cada ordem atrasada (RN07).
- `tela_executar(dados)`: executa o MRP e substitui as ordens planejadas.
- `tela_registro(dados)`: mostra o registro de um item. Recalcula o MRP, portanto está sempre atualizado.

Em resumo, para o vídeo: o MRP desce a estrutura. Começa na demanda das bicicletas e vai calculando o que falta em cada nível, até as matérias-primas, sempre respeitando estoque, lote e prazo.

## 10. ordens.py

Papel: ordens de produção e de compra. Requisitos: RF09, RF10, RF11 e RN08.

Importa: `estoque`, `estrutura`, `utils`.

Constante:

- `PROXIMO_STATUS`: para qual status cada ordem pode avançar.

```
PLANEJADA -> FIRME -> LIBERADA -> ENCERRADA
```

Como cada status aponta para um único seguinte, não é possível pular etapas nem voltar. `ENCERRADA` não é chave do dicionário, portanto dali não se avança.

Lógica:

- `definir_tipo(codigo)`: OC para matéria-prima, OP para item fabricado.
- `gerar_numero(ordens, tipo)`: encontra o maior número usado e soma 1. `:04d` formata com quatro dígitos.
- `substituir_planejadas(dados, sugestoes)`: apaga as ordens planejadas e cria as novas (RN08). Firmes, liberadas e encerradas permanecem.
- `filtrar_ordens(ordens, status, tipo)`: filtra por status e, se informado, por tipo.
- `buscar_ordem(ordens, numero)`: devolve a ordem ou lança erro.
- `validar_avanco(ordem, novo_status)`: garante que a ordem siga o ciclo.
- `avancar_ordens(ordens, numeros, novo_status)`: muda o status de uma ou mais ordens. Busca todas, valida todas e só então muda. Se uma falhar, nenhuma muda.
- `calcular_consumos(estrutura, ordem)`: calcula o consumo de cada componente direto.
- `listar_faltas(estoque, consumos)`: lista os componentes sem saldo suficiente.
- `apontar_producao(dados, ordem)`: baixa os componentes, dá entrada no item e encerra a OP (RF11).
- `receber_compra(dados, ordem)`: dá entrada no material e encerra a OC.

Sequência de `apontar_producao`:

```
1. é uma OP?
2. está LIBERADA?
3. o item tem estrutura?
4. há saldo de todos os componentes?
5. só então: baixa os componentes, dá entrada no produto e encerra
```

Se conferisse e baixasse um componente por vez, uma falta no último deixaria os primeiros já baixados, sem produção.

O consumo é apenas dos componentes diretos. A bicicleta consome a roda pronta; os raios foram consumidos quando a roda foi feita.

Telas:

- `descrever_status(ordem)`: mostra ATRASADA na ordem planejada que perdeu o prazo.
- `exibir_ordens(ordens)`: mostra uma tabela de ordens. Também é usada pelo `mrp.py`.
- `exibir_opcoes(ordens, status, tipo)`: mostra as ordens disponíveis e informa se há alguma.
- `avancar_pela_tela(dados, status_atual)`: parte comum de firmar e liberar.
- `tela_listar(dados)`: lista todas as ordens.
- `tela_firmar(dados)`: firma ordens planejadas.
- `tela_liberar(dados)`: libera ordens firmes.
- `tela_apontar(dados)`: aponta a produção de uma OP.
- `tela_receber(dados)`: recebe uma OC.

Em resumo, para o vídeo: o ciclo de status é um dicionário, e o apontamento é "tudo ou nada". O MRP só mexe nas planejadas; a partir de FIRME, a decisão é do planejador.

## 11. capacidade.py

Papel: centros de trabalho, roteiros e CRP. Requisitos: RF06, RF12 e RN09.

Importa: `estoque`, `itens`, `mps`, `utils`.

O MRP diz o que fazer sem verificar se cabe. O CRP compara as horas necessárias (carga) com as disponíveis (capacidade).

Lógica de centros e roteiros:

- `validar_codigo_centro(codigo)`: confere o formato `CT-01`.
- `buscar_centro(centros, codigo)`: devolve o centro ou lança erro.
- `gravar_centro(centros, codigo, campos)`: inclui ou altera. A capacidade precisa ser maior que zero, porque é divisor no cálculo do uso.
- `buscar_fabricado(itens, codigo)`: devolve um item PA ou SA.
- `gravar_roteiro(dados, cod_item, cod_centro, tempo)`: valida item, centro e tempo antes de gravar.

Lógica de carga:

- `calcular_carga(dados, cod_centro)`: soma as horas de cada semana (RN09).
- `listar_sobrecargas(cargas, capacidade)`: devolve as semanas em que a carga supera a capacidade. Carga igual à capacidade não é sobrecarga.
- `listar_sem_roteiro(dados)`: devolve os itens fabricados sem roteiro. Sem este aviso, a carga deles seria zero sem ninguém perceber.

Trecho principal de `calcular_carga`:

```python
for ordem in dados["ordens"]:
    roteiro = dados["roteiros"].get(ordem["codigo"])
    if not roteiro or roteiro["centro"] != cod_centro:
        continue
    semana = ordem["semana_liberacao"]
    if ordem["status"] != "ENCERRADA" and 1 <= semana <= SEMANAS:
        cargas[semana - 1] += ordem["quantidade"] * roteiro["tempo"]
```

As OCs são descartadas no primeiro `if`, pois matéria-prima não tem roteiro. Exemplo na semana 3 do `CT-03`: uma OP de 40 bicicletas x 0,5 h = 20 h, para uma capacidade de 16 h.

Telas:

- `formatar_horas(valor)`: sempre com uma casa decimal.
- `tela_cadastrar_centro(dados)`: inclui ou altera um centro.
- `tela_listar_centros(dados)`: lista os centros.
- `tela_cadastrar_roteiro(dados)`: inclui ou altera um roteiro.
- `tela_listar_roteiros(dados)`: lista os roteiros.
- `exibir_sem_roteiro(dados)`: mostra o aviso de itens sem roteiro.
- `exibir_carga(dados, centro)`: mostra a tabela de um centro, com uma barra de `#` a cada 10% de uso.
- `tela_carga(dados)`: mostra todos os centros.

Em resumo, para o vídeo: a carga é calculada na semana de liberação da OP, o que reproduz o exemplo 6.6 do enunciado. O sistema sugere, mas não move ordens sozinho.

## 12. custos.py

Papel: custo padrão. Requisito: RF13.

Importa: `capacidade`, `estrutura`, `itens`, `utils`.

```
custo do item = custo dos componentes + mão de obra
mão de obra   = horas por unidade x custo-hora do centro
```

Lógica:

- `multiplicar(quantidade, valor)`: multiplica e arredonda para centavos. Centraliza o arredondamento, para que a soma das linhas coincida com o total.
- `calcular_mao_de_obra(dados, codigo)`: tempo do roteiro vezes o custo-hora do centro.
- `calcular_materiais(dados, codigo)`: soma o custo dos componentes.
- `calcular_custo(dados, codigo)`: custo total de uma unidade.
- `listar_fabricados(itens)`: códigos dos itens PA e SA.
- `listar_pendencias(dados, codigo)`: usa `explodir` para encontrar itens sem estrutura, sem roteiro ou sem custo.

Trecho principal:

```python
def calcular_custo(dados, codigo):
    item = dados["itens"][codigo]
    if item["tipo"] == "MP":
        return item["custo"]
    materiais = calcular_materiais(dados, codigo)
    mao_de_obra = calcular_mao_de_obra(dados, codigo)
    return round(materiais + mao_de_obra, 2)
```

`calcular_custo` chama `calcular_materiais`, que chama `calcular_custo` para cada componente. É uma recursão indireta. Ela para na MP, cujo custo vem do cadastro, e sempre termina porque a RN03 impede ciclos.

```
PA-001
  SA-010 x 1
    MP-100: 3 x 22,00       =  66,00
    MP-101: 0,5 x 44,00     =  22,00
    mão de obra: 1 x 40,00  =  40,00    total 128,00
  SA-020 x 2
    MP-200: 1 x 45,00       =  45,00
    MP-201: 36 x 0,80       =  28,80
    MP-202: 1 x 46,00       =  46,00
    mão de obra: 0,5 x 40   =  20,00    total 139,80 x 2 = 279,60
  MP-300 x 1                =  45,00
  MP-301 x 1                = 320,00
  mão de obra: 0,5 x 40     =  20,00
                      total = 792,60
```

Telas:

- `exibir_componentes(dados, codigo)`: uma linha por componente.
- `exibir_mao_de_obra(dados, codigo)`: linha da mão de obra, se houver roteiro.
- `tela_detalhar(dados)`: custo detalhado de um item.
- `tela_resumo(dados)`: custo de todos os itens fabricados.

Em resumo, para o vídeo: o custo sobe das matérias-primas até o produto. Se o raio passar de R$ 0,80 para R$ 0,90, a bicicleta passa de R$ 792,60 para R$ 799,80, pois são 36 raios por roda e 2 rodas.

## 13. relatorios.py

Papel: exportação em CSV. Requisito: RF14.

Importa: `custos`, `estoque`, `itens`, `utils`.

Constantes:

- `CABECALHO_ESTOQUE` e `CABECALHO_ORDENS`: títulos das colunas, na mesma ordem dos valores.

Lógica:

- `montar_linha_estoque(dados, codigo)`: monta a linha de um item, com saldo, situação, custo e valor total.
- `montar_linha_ordem(dados, ordem)`: monta a linha de uma ordem.
- `gravar_csv(nome, cabecalho, linhas)`: grava qualquer tabela em CSV.
- `exportar_estoque(dados)`: exporta `posicao_estoque.csv`.
- `exportar_ordens(dados)`: exporta `lista_ordens.csv`.

Pontos importantes de `gravar_csv`:

- `with open(...)` fecha o arquivo automaticamente, mesmo em caso de erro.
- `newline=""` evita linhas em branco entre os registros no Windows.
- `encoding="utf-8-sig"` permite que o Excel reconheça os acentos.
- `delimiter=";"` é usado porque a vírgula já é o separador decimal.
- Um `OSError`, como o arquivo aberto no Excel, é convertido em `ValueError`, que o menu sabe mostrar.

Telas:

- `tela_estoque(dados)`: exporta a posição de estoque.
- `tela_ordens(dados)`: exporta a lista de ordens.

Em resumo, para o vídeo: o módulo reaproveita o saldo, a situação e o custo calculados nos outros módulos. Ele só organiza e grava.

## 14. graficos.py

Papel: gráficos de gestão. Requisito: RF16.

Importa: `capacidade`, `estoque`, `itens`, `mps`, `mrp`, `utils` e a biblioteca `matplotlib`.

Constantes:

- `AZUL`, `LARANJA`, `VERMELHO`, `CINZA`, `ESCURO` e `GRADE`: cores. O vermelho é reservado para alertas.
- `EIXO_SEMANAS`: números de 1 a 8.

A importação do matplotlib está protegida por `try` e `except ImportError`. Sem a biblioteca, `plt` recebe `None`, e o restante do sistema funciona.

Apoio:

- `verificar_biblioteca()`: avisa se o matplotlib não estiver instalado.
- `formatar_eixo(valor, _)`: números dos eixos com vírgula.
- `criar_figura(titulo, rotulo_x, rotulo_y, altura)`: cria a figura com o estilo padrão.
- `colocar_legenda(eixo, simbolos)`: coloca a legenda abaixo do gráfico, para não cobrir as barras.
- `finalizar(figura, nome)`: salva o PNG, mostra na tela e fecha a figura. O `finally` fecha a figura mesmo se houver erro.
- `contar_ordens(ordens, tipo)`: conta as ordens em aberto por semana de entrega.

Gráficos:

- `desenhar_estoque(dados)`: saldo e estoque de segurança de cada item, em barras horizontais. Usa escala logarítmica porque 4500 raios esmagariam as outras barras, e escreve o valor do saldo.
- `desenhar_projetado(dados, item)`: linha do estoque projetado e linha tracejada da segurança.
- `desenhar_ordens(dados)`: barras empilhadas. O empilhamento é feito com `bottom=producao`, que inicia as barras de compra onde terminam as de produção.
- `desenhar_carga(dados, centro)`: carga por semana e linha da capacidade. As semanas com sobrecarga ficam em vermelho.

Telas:

- `tela_estoque(dados)`: gráfico de posição de estoque.
- `tela_projetado(dados)`: gráfico de estoque projetado de um item.
- `tela_ordens(dados)`: gráfico de ordens por semana.
- `tela_carga(dados)`: gráfico de carga de um centro.

Em resumo, para o vídeo: os gráficos usam as mesmas funções de cálculo das telas, portanto os números nunca divergem. O PNG é salvo antes de abrir a janela, para existir mesmo se ela não puder ser aberta.

## 15. persistencia.py

Papel: leitura e gravação dos dados. Requisitos: RF15 e RNF07.

Importa: nenhum módulo do projeto.

Constantes:

- `PASTA_DADOS`: pasta `data`, ao lado do código. Usa `pathlib`, que funciona no Windows e no Linux.
- `ARQUIVOS_JSON`: nome de cada arquivo e o tipo de dado que ele guarda.
- `CAMPOS_MOVIMENTO`: colunas do `movimentos.csv`.

Leitura:

- `ler_json(nome, tipo)`: lê um arquivo. Se não existir, devolve um dado vazio do tipo certo. Se estiver corrompido, lança erro informando qual é.
- `converter_movimento(linha)`: converte os números, pois no CSV tudo é texto.
- `ler_movimentos()`: lê o histórico com `csv.DictReader`, que devolve cada linha como dicionário.
- `carregar_dados()`: lê todos os arquivos e monta o dicionário `dados`.

Gravação:

- `gravar_json(nome, conteudo)`: grava em um arquivo temporário e só depois substitui o original.
- `gravar_movimentos(movimentos)`: grava o histórico da mesma forma.
- `salvar_dados(dados)`: grava tudo.

Trecho principal:

```python
temporario = PASTA_DADOS / f"{nome}.tmp"
with open(temporario, "w", encoding="utf-8") as arquivo:
    json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
temporario.replace(PASTA_DADOS / f"{nome}.json")
```

Abrir um arquivo com `"w"` apaga seu conteúdo imediatamente. Se houvesse uma falha no meio, o antigo e o novo se perderiam. Com o temporário, o original fica intacto até o novo estar completo.

Em `salvar_dados`, o histórico é gravado primeiro. É o arquivo com maior chance de estar bloqueado (aberto no Excel) e, se falhar, o saldo novo não é gravado sem o histórico correspondente.

Em resumo, para o vídeo: JSON para os cadastros, que têm dados dentro de dados, e CSV para o histórico, que é uma tabela. A gravação é segura e automática.

## 16. utils.py

Papel: validação de entradas e formatação. Requisito: RNF05.

Importa: nenhum módulo do projeto.

Constante:

- `PASTA_SAIDA`: pasta `docs`, onde ficam os relatórios e gráficos.

Formatação:

- `montar_mensagem(rotulo, atual)`: monta a pergunta. Se houver valor atual, mostra entre colchetes.
- `formatar_numero(valor)`: usa vírgula e remove zeros sobrando. `0.5` vira `0,5` e `100` continua `100`.
- `formatar_moeda(valor)`: duas casas decimais e vírgula.
- `formatar_colunas(valores, largura)`: coloca números lado a lado, alinhados.
- `data_hoje()`: data atual no formato dia/mês/ano.
- `caminho_saida(nome)`: caminho de um arquivo na pasta de saída, que é criada se não existir.

Leitura:

- `ler_texto(rotulo, atual)`: não aceita vazio, a não ser que haja valor atual para manter.
- `ler_escolha(rotulo, opcoes)`: repete até receber uma das opções.
- `ler_inteiro(rotulo, atual, minimo)`: lê um inteiro. `int("abc")` lança `ValueError`, que é tratado, e a pergunta se repete.
- `ler_decimal(rotulo, atual, minimo)`: aceita vírgula ou ponto. Recusa `nan` e `inf` com `math.isfinite`, pois o Python os aceita como números e eles estragariam os cálculos.

Em resumo, para o vídeo: toda entrada do usuário passa por essas funções. Nenhum dado inválido chega à lógica por digitação.

## 17. Recursos de Python usados

| Recurso | Para que serve | Onde aparece |
|---|---|---|
| Função guardada em variável | Chamar depois, com `acao(dados)` | `menu.py` |
| Recursão direta | Função que chama a si mesma | `explodir`, `executar_menu` |
| Recursão indireta | Duas funções que se chamam | `calcular_custo` e `calcular_materiais` |
| Compreensão de lista | Filtrar ou transformar em uma linha | `filtrar_movimentos`, `listar_produtos` |
| Compreensão de dicionário | Montar um dicionário em uma linha | `iniciar_brutas`, `calcular_consumos` |
| Desempacotamento | `nivel, codigo, quantidade = linha` | `formatar_linha` |
| `**campos` | Copiar um dicionário para dentro de outro | `cadastrar_item`, `gravar_centro` |
| `.get(chave, padrão)` | Consultar sem erro se a chave não existir | `obter_saldo`, `obter_demanda` |
| `.setdefault` | Consultar e criar a chave se não existir | `gravar_componente` |
| `enumerate` e `zip` | Percorrer com posição; percorrer duas listas juntas | `ler_demanda`, `calcular_registro` |
| f-string com alinhamento | `{valor:>8}` alinha à direita em 8 espaços | Todas as tabelas |
| `raise ValueError` | Recusar uma operação | Lógica de todos os módulos |
| `raise ... from erro` | Trocar a mensagem e manter o erro original | `gravar_csv`, `ler_json` |
| `try` / `except` / `finally` | Tratar erros; executar sempre ao final | `executar_acao`, `finalizar` |
| `with open` | Fechar o arquivo automaticamente | `persistencia.py`, `relatorios.py` |
| Parâmetro com valor padrão | `atual=None`, `nivel=0` | `utils.py`, `explodir` |

## 18. Ajustes que podem ser pedidos

| Pedido | Onde alterar |
|---|---|
| Mudar o horizonte de semanas | `SEMANAS`, em `mps.py`. As demandas já salvas têm 8 valores e precisam ser recadastradas |
| Aceitar uma unidade nova | `UNIDADES`, em `itens.py` |
| Permitir códigos com quatro dígitos | `validar_codigo`, em `itens.py` |
| Incluir um status no ciclo | `PROXIMO_STATUS`, em `ordens.py` |
| Contar outro status como programado | `STATUS_PROGRAMADOS`, em `mrp.py` |
| Usar lote múltiplo em vez de lote mínimo | `calcular_lote`, em `mrp.py` |
| Somar as OPs atrasadas na semana 1 da carga | `calcular_carga`, em `capacidade.py` |
| Incluir custos indiretos | `calcular_custo`, em `custos.py` |
| Acrescentar uma coluna no relatório | Cabeçalho e função `montar_linha_`, em `relatorios.py` |
| Mudar uma cor ou um gráfico | Constantes e funções `desenhar_`, em `graficos.py` |
| Incluir uma opção de menu | Dicionário correspondente, em `menu.py` |

## 19. Perguntas e respostas

Por que um único dicionário `dados`, e não variáveis globais?
Porque cada função declara o que recebe. Fica claro quem usa o quê, e é possível testar com dados diferentes.

Por que o saldo não fica dentro do item?
Porque o saldo só pode mudar por movimentação. Separado, a tela de alteração de itens não tem como modificá-lo.

Por que processar PA, SA e MP nessa ordem?
Para que todos os pais já tenham somado suas necessidades quando chegar a vez do componente.

Por que a semana 6 da `SA-020` pede 80 se faltam 20?
Porque o lote mínimo é 80, e a RN06 determina o maior valor entre a necessidade líquida e o lote.

O que acontece com uma ordem FIRME quando o MRP é executado de novo?
Ela permanece e passa a contar como recebimento programado. Só as PLANEJADAS são apagadas.

Por que a necessidade da `SA-020` na semana 1 é 60, se há também uma OP atrasada de 10 bicicletas?
Porque a liberação dela cairia na semana 0, fora do quadro. O exemplo 6.4 do enunciado também mostra 60. A ordem aparece como mensagem de exceção.

O que acontece se faltar um componente no apontamento?
Nada é movimentado. O sistema lista tudo o que falta, e a OP continua liberada.

Como a RN10 é garantida?
Não existe função para editar ou apagar movimentos. Só se acrescenta à lista, e as correções são feitas por ajuste.

Por que os ciclos na estrutura são impossíveis?
Porque o componente é sempre de um tipo abaixo do pai: PA aceita SA e MP, SA aceita MP, e MP não aceita nada.

O que acontece se faltar energia durante o salvamento?
O arquivo original continua completo, porque só é substituído depois que o temporário termina de ser gravado.

O sistema funciona sem o matplotlib?
Sim. Só os gráficos ficam indisponíveis, com uma mensagem informando como instalar.