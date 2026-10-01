# Começar a implementação

## Prompt para colar no Astra

> Implemente integralmente a fixture Aurum descrita neste diretório. Comece por AGENTS.md e siga o backlog até o fechamento. Crie uma aplicação C17 de verdade, complexa, determinística, com todas as regras Gherkin executáveis e rastreabilidade bidirecional entre regras, código e testes. Preserve a independência do oráculo e exporte um pacote de análise sem respostas esperadas. Use autonomia para decisões de implementação, inicialize Git local e faça commits coerentes; não crie remote. Não reduza o escopo a um protótipo menor. Valide o que executar e registre honestamente o que continuar pendente.

## O que já existe

A aplicação C17, a CLI, o harness Gherkin oficial, os testes independentes, a rastreabilidade e os scripts de exportação/qualificação estão implementados. Comece pelo README.md para executar e por PROGRESS.md para conferir os gates e limites reais.

`make test-fast` executa a regressão obrigatória rápida; `make test-full` inclui mutações, sanitizers, cobertura, exportação isolada e Joern. `python tools/check_spec.py` continua sendo apenas verificação editorial; seu sucesso isolado não significa execução financeira nem qualidade de slicing.

## Continuidade

Mantenha contratos, catálogo e Gherkin concordantes. Para mudanças, leia apenas os contratos/catálogos/features afetados, preserve o oráculo e regenere os mapas depois de alterar código. A arquitetura e o backlog descrevem o escopo integral já entregue; não autorizam redução das capacidades em futuras alterações.
