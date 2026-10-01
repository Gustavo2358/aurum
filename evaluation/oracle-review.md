# Revisão independente dos exemplos de interação

A revisão abaixo foi escrita antes da primeira execução de `harness/adversarial.py`.
As referências numéricas usam inteiros arbitrários de Python, diretamente das
fórmulas de DOMAIN/OPERATIONS; não importam a biblioteca C, suas saídas ou seus
algoritmos. Resultados de transições são literais derivados dos componentes.
Isto constitui uma segunda implementação das fórmulas pequenas, com contraprovas
executáveis. Não é uma revisão humana nem uma prova de correção universal.

| Regras revistas | Fronteira e contraprova independente | Grupo executável |
|---|---|---|
| BR-MNY-006, BR-PRC-002 | FX usa `(nominal*taxa+5000)//10000`; taxas não inteiras e valores grandes não dependem de float | quote_reference |
| BR-PRC-004, BR-PRC-005, BR-PRC-006 | País não ativa tarifa; PREMIUM remove somente componente internacional; tarifa parcelada permanece | quote_reference |
| BR-PRC-007 | Tarifa final usa teto depois da soma das componentes | quote_reference |
| BR-INS-001, BR-INS-002, BR-INS-003 | n=0/1/3/4/12/13, país externo e piso por parcela são predicados distintos | quote_reference |
| BR-LIM-002 | P=10000,F=200 exige crédito 10200; 10199 recusa e igualdade aprova | credit_boundaries |
| BR-LIM-003 | Principal 200000 é permitido mesmo com tarifa; 200001 excede operação | credit_boundaries |
| BR-LIM-004, BR-LIM-007 | Autorizar6000,cancelar,autorizar4000 esgota limite diário10000; novo1 recusa | daily_gross |
| BR-LIM-005 | Limite de quantidade3 admite três decisões, a quarta recusa | daily_gross |
| BR-AUT-001, BR-AUT-004 | Conta inativa vence crédito/risco, sem mudar projeção financeira | eligibility |
| BR-ELG-008 | PIN compara nominal: USD10000 semPIN passa; USD10001 semPIN recusa | eligibility |
| BR-RSK-001, BR-RSK-006 | Scores49/50/79/80 produzem aprovação/revisão/revisão/recusa | risk_window |
| BR-RSK-005, BR-LIM-008, BR-AUT-005 | A quarta tentativa usa três decisões anteriores; janela inclui t−60 e exclui t−61; REVIEW aumenta contagem sem principal | risk_window |
| BR-AUT-002, BR-AUT-003 | Aprovação10000+3 cria hold10003, dívida/pontos zero | capture_fragments |
| BR-CAP-003, BR-CAP-004, BR-CAP-005 | Capturas3333,3333,3334 de10000 comF3 levam tarifas0,1,2; hold termina0 e dívida10003 | capture_fragments |
| BR-INS-004, BR-INS-005, BR-INS-006 | P10001,F100,n3 agenda componentes3334/3334/3333 e34/33/33 em ciclos3/4/5 | future_refund |
| BR-REV-006, BR-REW-006 | G200 em reembolsos3333/3333/3334 devolve66/67/67; um ponto reverte0/0/1 | refund_fragments |
| BR-REV-007, BR-REV-008, BR-BIL-008, BR-BIL-010 | Depois de pagar3368, reembolsoP5000,F49 deixa dívida1684; emissão original3368 não muda | future_refund |
| BR-BIL-007 | Pagamento10000 em P10000,F200 quitaF200 e P9800; devolverP100/F2 produz dinheiro2 e dívida100 | payment_priority |
| BR-BIL-007, BR-REV-010 | Pagar1000 após multa1000 quita multa primeiro; reembolso integral da captura não recria nem devolve multa | payment_priority |
| BR-REW-004, BR-REW-007 | Cap3: concessão2,estorno1,concessão1; estorno não permite recuperar cap bruto | reward_cap |
| BR-REW-005 | Ciclo seguinte concede novamente dentro do cap daquele ciclo | reward_cap |
| BR-REW-008 | Uma captura10000 pontua1; partes3333/3333/3334 pontuam0 | capture_partition |
| BR-IDM-001, BR-IDM-002, BR-IDM-004, BR-IDM-007 | Replay retorna resposta original e não duplica efeitos; alteração conflita; namespace inclui operação | replay |
| BR-IDM-006 | Recusa de crédito permanece após liberação de hold; outra chave pode aprovar | declined_replay |
| BR-AUT-008, BR-CAP-007, BR-BAT-008 | Capacidades de chave/lotes/diário/recompensas e expiração múltipla recusam transição inteira | capacity |
| BR-REV-004, BR-AUT-006 | TTL7: t+6 permanece aberto, t+7 expira; sem expiração antecipada | expiration |
| BR-BAT-004 | Trocar operações de A1/A2 preserva projeções por conta | independent_accounts |
| FR-IO-006, FR-IO-007 | Linha8192 aceita;8193 rejeita linha completa, sem efeito de prefixo válido; próxima linha funciona | line_boundary |

Os grupos também verificam `RECONCILE` após as sequências, porém essa observação
do SUT é complementar: as decisões e projeções são comparadas a valores externos.
Relações metamórficas comparam execuções reais sob permutação de campos, consultas
intercaladas, particionamento de capturas/reembolsos, contas independentes e saltos
de relógio. Não exigem invariância falsa dos pontos sob divisão de captura.

`tools/mutations.py` altera somente cópias temporárias da produção e mantém este
oráculo e as asserções intactos. Seu relatório distingue mutante morto, sobrevivente,
falha de build e variante equivalente por renomeação local. O resultado da execução
fica em `artifacts/mutations.json`; ausência desse arquivo não significa aprovação.
