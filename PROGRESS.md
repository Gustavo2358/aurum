# Progresso

## Estado
PGC_FIXTURE_QUALIFIED, no escopo de qualificação definido em docs/ACCEPTANCE.md. B00–B15 concluídos. Nenhum gate obrigatório permanece NOT_RUN ou FAIL.

## Evidência executada
- `make test-fast` e `make test-full`: PASS.
- 111 BR + 12 FR; 296 cenários Gherkin contra C real, incluindo 12 fluxos públicos; zero skip/passo indefinido. 3 testes do próprio harness comprovam detecção de divergência, operação desconhecida e preestado inválido.
- 73 verificações de protocolo; 17 grupos adversariais financeiros; 16.887 casos numéricos independentes; 9 sequências com 540 comandos e 212.281 asserções de invariantes; 16 regressões de API/limites.
- 11 mutantes não equivalentes mortos; uma renomeação local equivalente passou. ASan/UBSan e detecção de vazamentos da CLI passaram.
- Rastreabilidade externa: 123 funções, 877 decisões, 123 critérios reais; zero regra, função ou decisão órfã. Há 36 interações revisadas com mais de uma função, 31 entre arquivos.
- Corpus por allowlist compilado isoladamente, sem oráculo. Joern 4.0.630: ingestão, locations das 123 funções e cinco sentinelas de dependência PASS.

## Entregas
`build/aurum`; `dist/analysis-subject/`; `dist/evaluation-oracle/`; `dist/criteria-public.json`; mapas em `evaluation/`. Uso em README.md. Resultados resumidos em artifacts/REPORT.md, comandos/versões em artifacts/full.json e detalhes de Joern em artifacts/joern-smoke/REPORT.md.

## Limitações verdadeiras
- O smoke Joern produziu slice de profundidade 4 com 302 nós e 435 arestas. No experimento posterior, profundidade 8 concluiu em 31,267 s com 353 nós e 521 arestas; profundidade 20 atingiu timeout de 30 minutos sem resultado. Nenhum desses testes comprova slicing completo ou extração correta de regras. Evidência: artifacts/joern-depth8/REPORT.md.
- O frontend relatou fallback de ordem em CFG para for/break/continue. Sentinelas e locations foram verificadas; não foi provada a correção de todas as arestas do CFG.
- Transações copiam o estado, com tempo e memória proporcionais às coleções. Não há objetivo de throughput de produção.
- Probes UNIT/COMPONENT incluem estado histórico preparado e fórmulas isoladas; sua alcançabilidade por comandos não é presumida. Os fluxos E2E usam apenas seed e comandos públicos.
- Cobertura não é total; caminhos de falha de alocação real e I/O raros não foram todos exercitados. Capacidades esgotadas foram testadas em múltiplas coleções, com rollback completo.
- Não houve extração de regras por LLM neste contexto, prova formal de equivalência ou alegação de generalização a sistemas reais. O extrator futuro precisa de contexto separado e acesso só ao sujeito/critério público.
