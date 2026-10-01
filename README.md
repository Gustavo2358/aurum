# Aurum — fixture financeira C para o PGC

Pacote inaugural **Lean Spec-Driven Development** para o Astra implementar uma aplicação complexa, determinística e integralmente documentada. O domínio é inteiramente sintético.

**Escopo já especificado:** 111 regras funcionais BR, 12 requisitos técnicos FR, 284 cenários de unidade/componente e 12 ciclos completos, totalizando **296 cenários Gherkin concretos**. Há 14 capacidades documentadas e 15 arquivos `.feature`. Não são contagens de código implementado ou testes de aplicação já aprovados.

Comece por [START_HERE](START_HERE.md) e [AGENTS](AGENTS.md). O escopo é completo desde a primeira entrega; não substituí-lo por uma demonstração com poucas regras.

## Conteúdo

| Entrada | Função |
|---|---|
| [Produto](docs/PRODUCT.md) | Recorte PGC, definição de regra funcional e escopo |
| [Domínio](docs/DOMAIN.md) | Fórmulas, entidades, taxas inventadas e tempo |
| [Arquitetura](docs/ARCHITECTURE.md) | Capacidades, limites e separação produção/oráculo |
| [Catálogo](docs/RULEBOOK.md) | Índice de todas as regras e Gherkin |
| [Ciclos completos](docs/oracle/FLOWS.md) | Sequências concretas, inclusive cap com 80 comandos |
| [Contratos](docs/contracts/INDEX.md) | Operações, estado, interface, Joern e rastreabilidade |
| [ADRs](docs/adr/INDEX.md) | Oito decisões materiais |
| [Backlog](backlog/BACKLOG.md) | B00–B15, todos PENDING |
| [Testes](docs/TESTING.md) | Fronteiras, sequências, mutações e independência |
| [Aceitação](docs/ACCEPTANCE.md) | Gates funcional, oracle, corpus e Joern |
| [Progresso](PROGRESS.md) | Estado de retomada honesto |

## Regras, código e teste

O pacote exige rastreabilidade **regra → código → teste** e **código → documentação**. Infraestrutura também deve ter contrato, mas não se inventa regra financeira para cada linha. O core não lê o catálogo e não contém tags ou narrativas que entreguem o gabarito.

O agente deve produzir uma aplicação C normal, não um executor de `.feature`. Exportação para extração é por allowlist e sem oráculo. O suporte Joern é qualificado separadamente: parse bem-sucedido não prova slice completo.

## Uso imediato

Extraia o ZIP, abra o diretório no agente e cole o prompt de START_HERE. Inicialização de Git local é autorizada; remote/publicação não são. Não há aplicação C, bindings nem CPG prontos neste pacote. O script `tools/check_spec.py` verifica somente a integridade deste material.

```bash
python tools/check_spec.py
# Para validar também a sintaxe Gherkin:
python -m pip install gherkin-official
python tools/check_spec.py --gherkin
```

As dependências acima são do verificador/harness, não do produto C. Confira [PACKAGE_CHECK](PACKAGE_CHECK.md) para o que foi realmente validado na geração do pacote.
