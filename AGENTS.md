# Aurum — instruções para o agente

Você vai implementar uma aplicação financeira sintética e complexa em **C17**, usada como fixture de extração de regras no PGC. Este é o pacote inaugural, não uma implementação existente. Implemente o escopo completo; não o substitua por uma demonstração com algumas regras.

## Comece aqui

Leia `START_HERE.md`, `docs/PRODUCT.md`, `docs/DOMAIN.md`, `docs/ARCHITECTURE.md` e `backlog/BACKLOG.md`. Para cada capacidade, carregue somente seu contrato, seu catálogo de regras e seus arquivos Gherkin. `PROGRESS.md` é um resumo de retomada, não um diário.

## Autoridade e decisões

Contratos de comportamento e Gherkin são normativos e precisam concordar. `docs/RULEBOOK.md` indexa o catálogo. ADRs registram decisões arquiteturais, não podem revogar silenciosamente regras. Uma contradição material deve ser registrada e resolvida explicitamente antes de implementar o comportamento afetado. Nunca altere uma expectativa para fazer o código passar. Exemplos não limitam uma regra universal ao conjunto de linhas da tabela.

## Autonomia

Escolha nomes, funções, estruturas internas, algoritmos, build e organização de testes. A arquitetura estabelece fronteiras, não um diagrama de classes obrigatório. Não peça autorização por decisão reversível. Use ADR novo apenas para decisão material. Pode paralelizar capacidades com contratos compartilhados estabilizados e responsáveis claros. Não fabrique integrações ao unir trabalho paralelo.

Inicialize Git local se não existir, faça commits de unidades coerentes e mantenha o estado retomável. Não crie remote nem publique sem pedido. Não use código, dados ou regras do banco do usuário. Não adicione produtos financeiros, regulamentos ou políticas reais: todo o domínio aqui é inventado.

## Regras inegociáveis

- Todo comportamento implementado deve ter regra, contrato ou requisito documentado; toda função/ramificação relevante deve ter rastreabilidade inversa. Código auxiliar liga-se ao contrato funcional/técnico que serve, sem inventar uma regra de negócio por linha.
- O oráculo é escrito antes da implementação e não pode ser calculado pela aplicação sob teste. Step definitions só preparam estado, chamam o C real e comparam resultados.
- O core não lê `.feature`, catálogo, expectativas, matrizes nem nomes de casos. Nenhum ID `BR-*`, `FR-*`, `SC-*` ou narrativa Gherkin em `subject/`.
- Toda lógica financeira permanece em C comum: não implemente um interpretador de regras carregadas da documentação, nem uma tabela de respostas por cenário.
- Sem UB, overflow silencioso, float para dinheiro, relógio implícito, aleatoriedade não controlada, rede ou dependência de locale.
- Erros financeiros não podem deixar efeitos parciais. Contabilidade, reservas, parcelas, estornos, pontos e idempotência devem concordar.
- Use o parser oficial de Gherkin no harness, não um parser por regex. Cenário não implementado, passo indefinido, skip ou fixture vazia falha no gate obrigatório.
- O pacote de análise exportado contém somente código de produção e dependências de build estritamente necessárias. O oráculo e as respostas esperadas ficam fora.
- Não confunda sucesso de parse/CPG no Joern com correção de slicing. Relate as duas coisas separadamente.
- Nunca declare PASS de comando não executado. Falta de ferramenta é `NOT_RUN`, e o gate correspondente continua aberto.

## Ciclo de entrega

Regra → fronteiras e contraprova → exemplos revisados → implementação → testes → rastreabilidade → regressão. Execute FAST a cada unidade e FULL ao fechar. Preserve evidência pequena e reproduzível. Não produza certificados, pins de commits, pilhas de versões documentais ou relatórios administrativos por etapa. Registrar versões realmente usadas na execução final é reprodutibilidade, não autorização para burocracia.

O trabalho termina somente com os gates de `docs/ACCEPTANCE.md`, todos os itens obrigatórios do backlog e as limitações verdadeiras em `PROGRESS.md`. Não encerre após implementar só o caminho feliz ou só a primeira vertical.
