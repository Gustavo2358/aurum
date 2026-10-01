# Experimento nativo de slicing: profundidade 12

A profundidade **12 concluiu em 176,365 segundos (2min56s)**, com exit 0, dentro do limite de 900 segundos. Foi usada a mesma consulta `capture_apply` / `ledger_pair`, com paralelismo 2 e o mesmo CPG das tentativas 8 e 20. O hash do CPG foi conferido contra os três registros.

| Profundidade | Tempo observado | Estado | Nós | Arestas |
|---|---:|---|---:|---:|
| 4 | 4,86 s | Concluído no smoke original | 302 | 435 |
| 8 | 31,267 s | Concluído | 353 | 521 |
| 12 | 176,365 s | Concluído | 370 | 541 |
| 20 | 1.800,126 s | TIMEOUT, sem slice | — | — |

## Validação executada

O JSON de profundidade 12 tem 155.503 bytes. Foram conferidos JSON válido, coleções não vazias, unicidade dos IDs dos nós e existência das duas pontas de todas as arestas. Uma comparação adicional dos três resultados concluídos confirmou também ausência de arestas duplicadas.

Em relação à profundidade 8, todos os 353 nós e 521 registros de aresta foram preservados, com **17 nós e 20 arestas adicionais**. Em relação à profundidade 4, foram preservados todos os elementos, com 68 nós e 106 arestas adicionais. Nós foram comparados por ID; arestas, pelo registro JSON completo com chaves ordenadas. Essas identidades valem para este CPG.

GNU time registrou pico de memória de 949.648 KiB (aproximadamente 927 MiB), 361,52 s de CPU de usuário e 2,01 s de sistema, com utilização média de 206%. A saída confirmou a gravação do slice; stderr contém os avisos de depreciação/acesso nativo do Java. Não havia processo Joern remanescente após a conclusão.

`make test-fast`: PASS nesta rodada, incluindo 296 cenários Gherkin contra C real e três testes do harness (299/299), 73 verificações de protocolo, checagem aritmética e rastreabilidade. FULL não foi reexecutado nesta rodada; sua evidência anterior permanece separada. Não houve mudança no código da aplicação nem no runner.

## Interpretação e pendências

Nesta execução, passar de profundidade 8 para 12 aumentou o tempo em aproximadamente 5,64 vezes e acrescentou 17 nós. É uma medição por profundidade, sem repetições para caracterizar variação. Não permite prever quando a profundidade 20 terminaria ou diagnosticar a causa de sua demora.

O slicing continua sendo a funcionalidade nativa do Joern. A extração de regras pelo método do PGC e a avaliação de suficiência semântica contra o oráculo continuam pendentes. A validação estrutural e o aumento do grafo não demonstram recuperação completa das regras.

## Reprodução e evidência

```sh
.venv/bin/python tools/joern_slice_trial.py --depth 12 --timeout-seconds 900
```

Preserve ou mova esta pasta antes de repetir: o script recusa sobrescrever um slice existente. [summary.json](summary.json) contém o comando exato, datas UTC, hashes, duração, exit e validação estrutural. Saídas: [stdout.log](stdout.log), [stderr.log](stderr.log), [resources.txt](resources.txt) e [capture-slice.json](capture-slice.json). O [relatório anterior](../joern-depth8/REPORT.md) documenta a tentativa 20 e a limitação de sua coleta de recursos após timeout.
