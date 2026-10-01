# Oráculo autoral — não exportar para o extrator

Aqui estão os enunciados, exemplos e dados de referência para avaliar a aplicação e, futuramente, o extrator. 123 regras/requisitos; 284 exemplos de contrato e 12 ciclos completos.

`catalog/*.md` e `features/*.feature` são legíveis; `rules.json` e `flows.json` são o inventário estruturado equivalente para checks e harness. Não há tabelas de respostas no runtime de produção. Alterações precisam manter todas essas representações coerentes.

Os artefatos foram escritos antes de existir implementação C. Isso éreferência independente do código futuro, não garantia absoluta de ausência de erros autorais. Revise exemplos contraditórios antes de implementar, com justificativa; jamais editar o padrão só para passar um teste.

Consulte [PROBES](PROBES.md), [FLOWS](FLOWS.md) e [contrato de rastreabilidade](../contracts/ORACLE_AND_TRACEABILITY.md).
