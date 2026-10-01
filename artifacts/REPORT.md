# Fechamento Aurum

Estado: **PGC_FIXTURE_QUALIFIED** dentro dos gates da fixture. FAST e FULL executados com PASS. Nenhum gate obrigatório NOT_RUN.

## Produto

C17, biblioteca padrão, API e CLI com todas as capacidades do catálogo. Dinheiro inteiro verificado, relógio explícito, transação por estado privado e commit único, diário balanceado e projeções reconciliadas. Git local, sem remote.

```sh
make all
./build/aurum --seed examples/seed.txt --commands examples/commands.txt
make test-fast
make test-full
```

## Gates e evidências

| Gate | Resultado | Evidência |
|---|---|---|
| F — funcional | PASS | 296 Gherkin, 12 fluxos públicos, 73 checks de protocolo, 17 grupos adversariais, sanitizers |
| T — oráculo e rastreabilidade | PASS | 123 regras, 123 funções, 877 decisões; zero órfão; 11 mutantes mortos; revisão independente |
| C — corpus | PASS | 11 arquivos por allowlist, build isolado e scan de vazamento |
| J — Joern | PASS com limites explícitos | 123 locations reconciliadas e cinco sentinelas; slice parcial de profundidade 4 |

Gherkin: 136 UNIT, 127 COMPONENT e 33 E2E. As 296 expectativas originais foram preservadas. Mais três testes conferem o próprio harness. Probes recebem apenas entradas; resultados esperados ficam fora do sujeito.

Aritmética independente: 16.887 casos, 32.502 asserções. Invariantes: 9 sequências, 540 comandos, 212.281 asserções. A revisão final acrescentou 11 casos de API inválida/serialização e 5 casos de limites numéricos/transacionais. As mutações tiveram 11 mortes, zero sobreviventes e uma renomeação equivalente aprovada.

Cobertura GCC, combinando CLI e API: **1194/1251 linhas (95.44%)**, **1289/1646 desfechos de branches (78.31%)**. Cobertura mede execução, separadamente da execução de cenários e da correção semântica. Falhas reais de alocação e certos erros de I/O permanecem fora da cobertura.

## Reprodutibilidade

Versões observadas: cc (Ubuntu 15.2.0-16ubuntu1) 15.2.0; Python 3.14.4; gherkin-official 42.0.1; libclang 18.1.1; Joern 4.0.630. As flags e comandos exatos, exits e logs estão em `full.json`, `sanitize.json`, `coverage.json` e `joern-smoke/summary.json`.

O build normal usa `-std=c17 -O2 -g -Wall -Wextra -Wpedantic -Werror`. ASan e UBSan executaram o mesmo Gherkin sobre a biblioteca C, além das sequências e regressões. A CLI foi executada com detecção de vazamentos; o processo Python usou detecção de vazamentos desligada para não atribuir alocações do interpretador ao produto.

## Rastreabilidade e exportação

`evaluation/` contém rule-index, traceability, scenario-index, inventory AST, criteria públicos/privados, expected-supports e interaction-evidence. Foram revisadas 36 regras com suporte causal em mais de uma função e 31 entre arquivos; wrappers não foram usados para inflar essas contagens.

`dist/analysis-subject/` contém apenas fontes C, header e Makefile. `dist/evaluation-oracle/` contém o material do avaliador. `dist/criteria-public.json` expõe locais e seletores de observação; `dist/manifest.json` contém os hashes da exportação. Nenhum ID de regra, Gherkin ou resultado esperado está no sujeito.

## Limites

A ingestão CPG, o mapeamento e as sentinelas passaram. O slice real tem 302 nós e 435 arestas, limitado à profundidade 4. A tentativa exploratória com profundidade 20 foi interrompida sem resultado. O frontend registrou fallbacks de CFG; ver `joern-smoke/REPORT.md`. Não há alegação de slicing completo ou de extração correta de todas as regras.

As transações copiam o estado e não oferecem garantia de throughput. Componentes históricos preparados são distinguidos de fluxos públicos. Não foi feita extração por LLM no contexto autoral, nem prova formal ou inferência de generalização para software real.

## Experimento posterior solicitado

Profundidade 8 concluiu em 31,267 segundos (353 nós, 521 arestas). Profundidade 20 atingiu timeout de 30 minutos sem gerar slice. O smoke de profundidade 4 acima permanece como evidência da execução FULL original. [Comparação e limites](joern-depth8/REPORT.md).
