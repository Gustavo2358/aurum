# Experimento nativo de slicing: profundidades 4, 8 e 20

A tentativa de profundidade **8 concluiu em 31,267 segundos**, com exit 0. A tentativa anterior de profundidade 20 atingiu o limite de 30 minutos e foi encerrada automaticamente (exit 124). Não houve nova execução de profundidade 20 após esse encerramento; o pedido seguinte alterou a profundidade para 8.

| Profundidade | Tempo observado | Estado | Nós | Arestas |
|---|---:|---|---:|---:|
| 4 | 4,86 s | Concluído no smoke anterior | 302 | 435 |
| 8 | 31,267 s | Concluído | 353 | 521 |
| 20 | 1.800,126 s | TIMEOUT, sem slice | — | — |

## Condições e validação

As tentativas 8 e 20 usaram o mesmo CPG, cujo SHA-256 está nos respectivos `summary.json`. Foi mantida a consulta nativa `joern-slice data-flow`, filtrando `capture_apply` e chamadas `ledger_pair`, com paralelismo 2. A profundidade 8 recebeu limite de 900 segundos e terminou antes dele.

O JSON de profundidade 8 tem 149.036 bytes. A validação conferiu JSON válido, coleções não vazias, unicidade dos IDs dos nós e existência das duas pontas de todas as arestas. Os 302 nós do resultado de profundidade 4 estão presentes; há 51 nós e 86 arestas adicionais. Essa comparação usa IDs do mesmo CPG, não identidades universais entre execuções de ingestão.

O pico de memória informado por GNU time para a execução concluída de profundidade 8 foi 1.034.484 KiB (aproximadamente 1.010 MiB). O tempo de CPU foi 65,67 s de usuário + 0,93 s de sistema, compatível com uso de cerca de dois núcleos.

No teste 20, as amostras de `ps` mostraram CPU perto de 205% e RSS perto de 785 MiB. Os números de CPU/RSS em `joern-depth20/resources.txt` **não representam o Java**: após o encerramento do grupo pelo timeout, o coletor externo registrou apenas os processos supervisores. Eles não devem ser usados para comparar memória/CPU entre profundidades. O tempo de parede e o exit 124 foram confirmados também pelo supervisor Python.

## Interpretação

A profundidade 8 é executável para essa consulta e esse CPG nas condições observadas. A profundidade 20 não concluiu em 30 minutos. Não foi diagnosticada a causa da demora, nem estimado quanto tempo adicional seria necessário.

É um experimento da funcionalidade nativa do Joern. Ainda não houve extração de regras pelo método do PGC nem avaliação de suficiência semântica dos slices contra o oráculo. Mais nós e arestas não demonstram recuperação completa das regras.

## Reproduzir e consultar

```sh
.venv/bin/python tools/joern_slice_trial.py --depth 8 --timeout-seconds 900
```

O script recusa sobrescrever um resultado existente. Preserve ou mova a pasta do resultado antes de repetir. Comando exato, datas UTC, hash do CPG, duração, exit e hash do slice estão em [summary.json](summary.json). Saída do processo: [stdout.log](stdout.log), [stderr.log](stderr.log) e [resources.txt](resources.txt). A tentativa de 30 minutos está em [joern-depth20/summary.json](../joern-depth20/summary.json).
