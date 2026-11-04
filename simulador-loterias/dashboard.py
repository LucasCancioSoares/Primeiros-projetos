"""Painel local experimental em Streamlit. Execute: streamlit run dashboard.py"""
import json
from pathlib import Path

import streamlit as st

from finance import make_tickets, simulate_portfolio
from integration import historical_report, load_panel, load_results, historical_payouts
from lottery import CONFIG

st.set_page_config(page_title="Laboratório de Loterias", page_icon="🎲", layout="wide")
st.title("Laboratório estatístico de loterias")
st.caption("Projeto experimental. Não prevê dezenas nem garante prêmio ou rentabilidade.")

try:
    panel = load_panel()
    results = load_results()
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Dados indisponíveis ou inválidos: {exc}")
    st.info("Execute a coleta em GitHub Actions ou localmente: python lottery.py update --backfill 10 && python agenda.py")
    st.stop()

st.caption("Última consulta à Caixa (UTC): " + str(panel.get("consultado_em_utc", "não informada")))
labels = {"lotofacil": "Lotofácil", "quina": "Quina", "megasena": "Mega-Sena"}
game = st.selectbox("Modalidade", list(CONFIG), format_func=lambda g: labels[g])
if game not in panel["modalidades"] or game not in results:
    st.error("Modalidade não consta do painel e/ou histórico.")
    st.stop()

entry = panel["modalidades"][game]
latest = entry["ultimo_resultado"]
upcoming = entry["proximo_sorteio"]
left, middle, right = st.columns(3)
left.metric("Último concurso apurado", str(latest["numero"]))
middle.metric("Próximo concurso informado", str(upcoming["concurso"]))
right.metric("Estimativa de prêmio (não garantida)",
             f"R$ {upcoming['estimativa_premio']:,.2f}" if upcoming.get("estimativa_premio") is not None else "Não informada")
st.write("**Resultado oficial:**", latest["data"], "—", ", ".join(f"{n:02d}" for n in latest["dezenas"]))
st.write("**Próximo sorteio informado:**", upcoming["data"])
st.subheader("Premiação do último concurso")
st.dataframe(latest["rateio"], use_container_width=True, hide_index=True)

st.divider()
st.subheader("Carteira experimental")
st.info("Custo é um valor que você fornece; não foi verificado para a data de cada concurso.")
stake = st.number_input("Custo hipotético por aposta simples (R$)", min_value=0.01, value=5.0, step=0.5)
budget = st.number_input("Orçamento por concurso (R$)", min_value=0.01, value=30.0, step=5.0)
quantity = min(int(budget // stake), 100)
if quantity < 1:
    st.warning("Orçamento insuficiente para uma aposta.")
    st.stop()
st.write(f"**{quantity} apostas simples distintas**, custo R$ {quantity * stake:.2f} por concurso.")
seed = st.number_input("Semente reprodutível", min_value=0, max_value=2**32-1, value=2026)
tickets = make_tickets(game, quantity, int(seed))
with st.expander("Ver apostas usadas nas análises"):
    st.dataframe([{"aposta": i+1, "dezenas": " ".join(map(str, sorted(t)))}
                  for i, t in enumerate(tickets)], hide_index=True)

mode = st.radio("Análise", ["Histórico observado", "Monte Carlo (cenário hipotético)"])
if mode == "Histórico observado":
    records = list(results[game].values())
    report = historical_report(game, tickets, float(stake), records)
    a, b, c = st.columns(3)
    a.metric("Concursos analisados", report["concursos"])
    b.metric("Lucro/prejuízo retrospectivo", f"R$ {report['lucro_total']:,.2f}")
    c.metric("Frequência histórica de lucro", f"{report['frequencia_historica_lucro']:.1%}")
    st.dataframe(report["detalhes"], use_container_width=True, hide_index=True)
    st.warning(report["aviso"])
else:
    st.warning("Usa as premiações do último concurso como cenário CONSTANTE e hipotético para todos os sorteios simulados. Isso não prevê os rateios futuros.")
    trials = st.slider("Quantidade de simulações", 100, 100000, 10000, step=100)
    payout_scenario = historical_payouts(latest)
    result = simulate_portfolio(game, tickets, float(stake), payout_scenario,
                                trials=trials, seed=int(seed))
    a, b, c = st.columns(3)
    a.metric("Lucro médio simulado", f"R$ {result['lucro_medio']:,.2f}")
    b.metric("Probabilidade simulada de lucro", f"{result['probabilidade_de_lucro']:.2%}")
    c.metric("Percentil de 5% do lucro", f"R$ {result['percentil_05_lucro']:,.2f}")
    st.json(result)

st.download_button("Exportar resultados da carteira (JSON)", data=json.dumps(
    {"modalidade": game, "carteira": [sorted(t) for t in tickets],
     "custo_informado": stake, "orcamento": budget,
     "fonte_painel": panel.get("consultado_em_utc")},
    ensure_ascii=False, indent=2), file_name="carteira_experimental.json",
    mime="application/json")
