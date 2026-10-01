# Verificação da fixture Aurum

Estado atual: **PGC_FIXTURE_QUALIFIED**, no escopo dos gates de [ACCEPTANCE](docs/ACCEPTANCE.md). A aplicação C17 e o harness estão implementados; B00–B15 estão concluídos. Os resultados abaixo resumem comandos efetivamente executados, com evidências em `artifacts/`.

| Verificação | Resultado real | Evidência |
|---|---|---|
| FAST e FULL | PASS | [full.json](artifacts/full.json) e logs dos comandos |
| Especificação e parser oficial Gherkin | PASS: 111 BR, 12 FR, 296 cenários, 15 features; IDs, catálogo, exemplos e links reconciliados | [FAST](artifacts/full-00.log) |
| Aplicação C, bindings e CLI | PASS: 296 cenários contra C real, incluindo 12 fluxos públicos; mais 3 testes do próprio harness; zero skip | [Gherkin](artifacts/gherkin-results.json) e [FAST](artifacts/full-00.log) |
| Protocolo e testes independentes | PASS: 73 verificações de protocolo, 17 grupos adversariais, 16.887 casos numéricos, 9 sequências com 540 comandos e 16 regressões de API/limites | [Adversariais](artifacts/adversarial.json), [numéricos](artifacts/numeric-properties.json), [invariantes](artifacts/invariants.json) e [regressões](artifacts/regression-audit.json) |
| ASan/UBSan | PASS nos testes executados, com detecção de vazamentos na CLI | [Sanitizers](artifacts/sanitize.json) |
| Mutações | PASS: 11 mutantes não equivalentes mortos; uma renomeação equivalente passou | [Mutações](artifacts/mutations.json) |
| Cobertura | 1.194/1.251 linhas (95,44%); 1.289/1.646 desfechos de branches (78,31%) | [Cobertura](artifacts/coverage.json) |
| Rastreabilidade bidirecional | PASS: 123 funções, 877 decisões e 123 critérios; zero regra, função ou decisão órfã | [Rastreabilidade](evaluation/traceability.json), [inventário AST](evaluation/inventory.json) e [FAST](artifacts/full-00.log) |
| Corpus isolado | PASS: exportação por allowlist e build sem oráculo | [Exportação](artifacts/full-08.log) e [build isolado](artifacts/export-build.txt) |
| Joern / CPG | PASS: ingestão, locations das 123 funções e cinco sentinelas de dependência, em gates separados | [Resumo Joern](artifacts/joern-smoke/summary.json) e [relatório](artifacts/joern-smoke/REPORT.md) |
| Slicing nativo Joern | Profundidades 4, 8 e 12 concluídas; profundidade 20 atingiu timeout de 30 minutos | [Comparação e limites](artifacts/joern-depth12/REPORT.md) |

## Alcance e pendências

A qualificação cobre a fixture e os gates definidos; não comprova extração completa de regras. A análise pelo método do PGC e a comparação semântica com o oráculo ainda não foram executadas. Geração de CPG, dependências selecionadas e validade estrutural dos slices são evidências distintas.

O frontend Joern relatou fallbacks de ordem no CFG. A cobertura não é total: falhas reais de alocação e certos erros de I/O não foram todos exercitados. Não há prova formal de equivalência nem garantia de generalização para sistemas reais. [PROGRESS.md](PROGRESS.md) reúne os limites atuais.

O check editorial não executa o C. A checagem aritmética dos exemplos usa um subconjunto independente de 84 casos e 106 comparações; os testes numéricos do FULL têm o alcance maior indicado acima. As expectativas ficam fora da aplicação e do pacote analisável.

## Reproduzir

Siga os requisitos e a instalação de dependências do [README](README.md), depois execute:

```sh
make test-fast
make test-full
```

Comandos individuais, versões e exits estão em [full.json](artifacts/full.json). Ferramenta ausente, falha ou teste não executado deve continuar explícito; este resumo só pode manter PASS enquanto a evidência se aplicar ao estado da fixture.
