# Joern smoke

Joern 4.0.630. Ingestion: PASS; source locations: PASS; selected dependence checks: PASS.

All 123 production functions match the independent Clang inventory in file, starting line and ending line. Each has a nonempty CFG. The frontend adds 15 synthetic initializers.

| Sentinel | Real call between files | Parameter→argument paths | Control nodes |
|---|---|---:|---:|
| authorization | authorize_apply → credit_admission | 1 | 20 |
| capture | capture_apply → cumulative_delta | 1 | 15 |
| refund | refund_apply → cumulative_delta | 2 | 26 |
| billing | invoice_minimum → ceil_rate | 1 | 2 |
| payment | pay_apply → project_account | 1 | 6 |

The five sentinels have real source locations, cross-file calls, control dependence and observable writes. Raw queries and path samples are in `inventory.json`; exact commands and timings are in `summary.json`.

## Slicing boundary

The bounded depth-4 `capture_apply`/`ledger_pair` argument slice returned 302 nodes and 435 edges (PASS). It is partial by construction. An exploratory depth-20 run was interrupted after minutes without output. This smoke does not establish completeness of memory, state or control support for all rules. The [official slicing documentation](https://docs.joern.io/cpg-slicing/) specifies backward slicing from call arguments.

The frontend emitted CFG order fallback warnings for for/break/continue. Selected dependence checks passed; uninspected CFG edges remain a frontend limitation. Java runtime deprecation/native-access warnings are preserved in stderr logs. No rule extraction was run in this implementation context.
