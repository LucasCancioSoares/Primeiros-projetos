# Simulador de Loterias — versão experimental

Projeto independente para Lotofácil, Quina e Mega-Sena. Busca minimizar o custo de apostas e avaliar retorno líquido, risco e cobertura, **sem alegar previsão dos sorteios**.

## Executar localmente

Requer Python 3.11+ (sem dependências externas):

```bash
cd simulador-loterias
python lottery.py simulate --game lotofacil --trials 100000 --seed 2026
python -m unittest discover -s tests -v
python lottery.py update --backfill 10
```

- `update`: busca o concurso recente de cada modalidade; `--backfill 10` carrega até os 10 últimos na primeira execução.
- `simulate`: compara frequências simuladas de acertos com a distribuição hipergeométrica exata.
- `data/resultados.json`: banco de resultados em JSON versionável; não é atualizado se a busca falhar antes de coletar qualquer dado.
- Para um futuro SQLite, usar JSON como fonte persistida no GitHub e reconstruir o banco em cada execução, sem depender do disco temporário do Actions.

## Agendamento

O arquivo `.github/workflows/loterias.yml` na raiz do repositório executa testes e atualiza o JSON diariamente. O agendamento só entrará em vigor após a integração do PR à branch `main`. O job requer permissão **Contents: write** para persistir dados.

## Limitações / próximos passos

1. O endpoint `servicebus2.caixa.gov.br` é hospedado pela Caixa, mas não possui contrato público de API estável; poderá falhar/bloquear GitHub runners. Não substituir silenciosamente por fontes não verificadas.
2. Se houver concursos faltantes, a rotina tenta recuperar os intervalos, mas pode falhar em dias de indisponibilidade; conferir logs do Actions. Backfill grande gera tráfego e deve ser realizado com cuidado.
3. A versão inicial **não calcula lucro real**: falta guardar preços das apostas vigentes por data, regras completas de rateio e um motor de carteiras para avaliar todas as faixas e a exposição ao risco.
4. Premiações históricas não devem ser usadas como se fossem conhecidas no momento da decisão de apostar.
5. Não fazer apostas reais a partir do programa. Há risco financeiro e valor esperado negativo nos jogos convencionais.
6. O projeto de notícias/notificações do ChatGPT é separado do workflow de ingestão.

Fonte técnica: https://servicebus2.caixa.gov.br/portaldeloterias/api
