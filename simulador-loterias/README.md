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

## Painel de resultados e próximos concursos

O fluxo automático consulta os **resultados realizados** e, na mesma execução, o **próximo concurso informado pela Caixa** de Lotofácil, Quina e Mega-Sena. Os dois tipos de dados são mantidos separados em `data/painel.json`: `ultimo_resultado` (com dezenas e rateios) e `proximo_sorteio` (número, data e estimativa do prêmio). A estimativa não é premiação confirmada.

Rodar manualmente após atualizar resultados:

```bash
cd simulador-loterias
python lottery.py update --backfill 10
python agenda.py
```

O painel exige que o último concurso do banco esteja de acordo com a consulta online: se a Caixa informar concurso mais recente que o armazenado, a geração falha em vez de misturar informações de datas diferentes. A rotina de coleta pode funcionar e ainda assim a segunda consulta falhar: nesse caso o GitHub Actions indicará erro e não gravará um painel incompleto. O agendamento usa UTC e pode sofrer atrasos do GitHub.

Não gerar dezenas futuras nem utilizar prêmios estimados como valores de retorno das simulações.

## Painel integrado de resultados e finanças

A interface Streamlit lê `data/painel.json` (último resultado, próximo concurso e prêmio estimado) e `data/resultados.json` (histórico e rateio por concurso). **Não usa estimativas de prêmio futuro como se fossem valores recebidos**.

Instalação e execução local:

```bash
cd simulador-loterias
python -m pip install -r requirements-dashboard.txt
streamlit run dashboard.py
```

Para análise financeira existem dois modos:

1. **Histórico observado:** avalia a mesma carteira em cada concurso guardado, com os pagamentos observados por faixa daquele sorteio e custo hipotético/constante informado manualmente; não equivale a lucro historicamente realizável sem preços vigentes à época.
2. **Monte Carlo:** sorteios aleatórios futuros hipotéticos, mantendo fixos os valores de rateio do último concurso exclusivamente para cenário demonstrativo; **não são valores de prêmios futuros**.

O painel não faz apostas, não recomenda dezenas, não prevê sorteios, nem foi publicado na internet como serviço público. Para acesso por navegador fora do computador é necessário implantar a aplicação Streamlit em serviço de hospedagem apropriado, considerando a privacidade do repositório e o acesso aos arquivos.
