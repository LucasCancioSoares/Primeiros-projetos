# Roadmap — Simulador Estatístico de Loterias

Objetivo: comparar estratégias com **mesmo orçamento**, maior chance de lucro líquido e risco controlado. Nenhum algoritmo prevê sorteios independentes nem promete lucro.

## Etapa 0 — Base (implementada, ainda sem validação no Actions)
- [x] Importação e validação de concursos da Caixa
- [x] Simulação Monte Carlo e probabilidades hipergeométricas exatas
- [x] GitHub Actions para atualização do histórico (necessita merge e execução real)
- [ ] Verificar conectividade com endpoint em runner GitHub e auditar lacunas
- [ ] Carga histórica completa, com limites de requisições e retomada segura

## Etapa 1 — Finanças (protótipo implementado)
- [x] Carteiras de apostas simples distintas, avaliadas no mesmo sorteio
- [x] Custo total, lucro médio, mediana, chance de lucro/prejuízo e percentil de perda
- [x] Testes de carteiras, entradas inválidas e reprodutibilidade
- [ ] Registro de preços vigentes por data da modalidade, com fontes e histórico
- [ ] Rateio real variável por concurso, análise de regras, tributos e premiações
- [ ] Intervalos de confiança e auditoria de precisão das estimativas

## Etapa 2 — Modelagem de dados
- [ ] SQLite com tabelas `concursos`, `dezenas`, `rateios`, `regras`, `execucoes`
- [ ] Chaves únicas por modalidade+concurso, transações e validação de integridade
- [ ] Origem, data de coleta, hash do registro, reprocessamento e correção de dados
- [ ] Backfill incremental e idempotente de todas as modalidades

## Etapa 3 — Otimização combinatória
- [ ] Comparação de estratégias **ao mesmo custo** e sem dezenas repetidas
- [ ] Cobertura de combinações: garantias combinatórias e limites matemáticos
- [ ] Pareto de custo, probabilidade de lucro, perda máxima e retorno esperado
- [ ] Separar otimização de cobertura de pretensões de previsão

## Etapa 4 — Validação científica
- [ ] Cenários aleatórios independentes; comparação com fórmulas exatas
- [ ] Validação fora da amostra e prevenção de data leakage
- [ ] Benchmarks e testes de regressão para volume de milhões de sorteios
- [ ] Documentar hipóteses, aleatoriedade, intervalos de confiança e limitações

## Etapa 5 — Interface e operações
- [ ] Painel Streamlit para modalidades, orçamento, carteira e cenários
- [ ] Relatórios CSV/JSON com custo, ROI, retorno esperado e risco
- [ ] Logs, monitoramento do workflow, alertas de coleta e notificações
- [ ] Integração documentada com o Radar de Loterias (alertas independentes)

**Estado atual:** protótipo experimental, sem apostas reais e sem recomendação de compras. O módulo financeiro usa pagamentos hipotéticos informados pelo operador, não dados confirmados de rateio futuro.
