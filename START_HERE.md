# Começar a implementação

## Prompt para colar no Astra

> Implemente integralmente a fixture Aurum descrita neste diretório. Comece por AGENTS.md e siga o backlog até o fechamento. Crie uma aplicação C17 de verdade, complexa, determinística, com todas as regras Gherkin executáveis e rastreabilidade bidirecional entre regras, código e testes. Preserve a independência do oráculo e exporte um pacote de análise sem respostas esperadas. Use autonomia para decisões de implementação, inicialize Git local e faça commits coerentes; não crie remote. Não reduza o escopo a um protótipo menor. Valide o que executar e registre honestamente o que continuar pendente.

## O que já existe

Especificação, arquitetura, ADRs, catálogo normativo, exemplos concretos Gherkin, contratos de execução/avaliação, backlog e um verificador estrutural do pacote. **Não há aplicação C implementada, bindings de execução, CPG, slices ou resultados de extração.**

`python tools/check_spec.py` verifica integridade editorial. `python tools/check_spec.py --gherkin` também exige o pacote Python `gherkin-official` e verifica a sintaxe com o parser oficial. Essas verificações não executam a aplicação futura.

## Ordem prática

Estabilize dinheiro/tempo/estado e o harness; desenvolva capacidades completas com testes; integre ciclos longos; finalize o corpus e os gates. As etapas são organização interna da construção, não versões menores do escopo. A entrega inaugural inclui todas as capacidades.

Para dúvidas locais, consulte primeiro o contrato correspondente. Registre uma decisão material em ADR, em vez de reabrir todo o projeto. O catálogo é o mínimo contratado; comportamento adicional exige documentação e teste antes de entrar no baseline.
