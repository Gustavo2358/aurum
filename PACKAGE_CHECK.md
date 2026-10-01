# Verificação do pacote de especificação

Data de preparação: 2026-09-30.

| Verificação | Resultado real |
|---|---|
| Integridade editorial (`python tools/check_spec.py`) | PASS: 111 BR, 12 FR, 296 cenários e 15 arquivos de features reconciliados |
| IDs e referências | PASS: IDs únicos e referências de regras dos fluxos existentes |
| Catálogo Markdown × JSON × Gherkin | PASS: enunciados e dados/expectativas dos exemplos concordam textualmente |
| Links relativos e cercas Markdown | PASS na execução final; nenhuma referência interna quebrada |
| Vetores numéricos (`python tools/check_oracle_math.py`) | PASS: 84 casos selecionados, 106 comparações, nenhuma divergência |
| Parser oficial Gherkin (`--gherkin`) | NOT_RUN: pacote indisponível no ambiente; instalação/download bloqueados por conectividade |
| Aplicação C e bindings | NOT_IMPLEMENTED: são o trabalho solicitado ao agente |
| Joern / CPG / slicing | NOT_RUN: ainda não há aplicação implementada a importar |

## Alcance dos checks

A reconciliação editorial é comparação de texto/dados e inventário lexical de tags, **não um parser Gherkin alternativo**. A checagem numérica usa cálculos independentes em Python sobre um subconjunto de vetores; não prova todas as regras, alcançabilidade, ausência de UB ou correção do código futuro. Os ciclos completos foram especificados, mas não executados contra C.

O verificador aceita `--gherkin` para usar o parser oficial assim que ele estiver disponível. Ausência do parser retorna código2, não PASS. A implementação precisa instalar a ferramenta, executar os cenários e qualificar a fixture conforme os gates. Não tratar a presente documentação como certificado de aplicação pronta.

## Reproduzir

```bash
python tools/check_spec.py
python tools/check_oracle_math.py
python -m pip install gherkin-official
python tools/check_spec.py --gherkin
```

Todos os checks deste arquivo dizem respeito ao pacote autoral. Nenhum ID de nó, localização de código ou resultado de extração foi inventado para preencher uma matriz futura.
