# Progresso

## Estado
IMPLEMENTATION_PENDING: core C17 e CLI completos; qualificação final em andamento.

## Verde executado
`make test-fast`: 296 cenários pelo parser oficial e C real, 2 testes de falha do harness, 72 verificações adversariais de protocolo, auditoria numérica de 84 casos/106 asserções e inventário AST sem referências quebradas. Os 12 fluxos executam o binário público. Nenhuma expectativa original foi alterada.

## Próximo trabalho
Revisar e consolidar rastreabilidade, mutantes, sanitizers, invariantes de preestado, exportação e sentinelas Joern; executar FULL e registrar versões reais.

## Limitações atuais
Primeira ingestão real Joern bem-sucedida. Isso ainda não fecha o gate J: locations e sentinelas estão em verificação. Transações copiam estado e não têm objetivo de throughput de produção. Probes de componentes podem usar história sintética válida localmente; alcance por comandos públicos é verificado separadamente nos fluxos.
