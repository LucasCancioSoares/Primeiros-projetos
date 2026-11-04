"""Executa cenário demonstrativo e persiste relatório para o Radar de Loterias."""
import datetime as dt
import json
import math
import os
from pathlib import Path

from finance import make_tickets, simulate_portfolio
from integration import historical_payouts, load_panel
from lottery import exact_probability

DEST = Path(__file__).parent / "data" / "simulacao_megasena.json"
CUSTO_REFERENCIA = 6.0
SEMENTE = 2026
EXECUCOES = 200_000


def build_report(panel, trials=EXECUCOES, seed=SEMENTE):
    source = panel["modalidades"]["megasena"]
    latest = source["ultimo_resultado"]
    prices = historical_payouts(latest)
    # Em concurso acumulado o prêmio principal tem valor observado 0,
    # que NÃO deve ser usado como estimativa de pagamento futuro.
    scenario_payouts = {4: prices.get(4, 0.0), 5: prices.get(5, 0.0)}
    ticket = make_tickets("megasena", 1, seed=seed)
    simulated = simulate_portfolio("megasena", ticket, CUSTO_REFERENCIA,
                                   scenario_payouts, trials=trials, seed=seed)
    return {
        "gerado_em_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fonte_concurso_referencia": int(latest["numero"]),
        "data_concurso_referencia": latest["data"],
        "proximo_concurso_informado": source["proximo_sorteio"]["concurso"],
        "metodologia": "Uma aposta simples de seis dezenas, sorteios uniformes independentes.",
        "custo_por_aposta_referencia": CUSTO_REFERENCIA,
        "custo_necessario_para_realizar_apostas": 0,
        "premios_hipoteticos_usados": scenario_payouts,
        "premio_sena": "não modelado; prêmio futuro desconhecido",
        "probabilidades_exatas_por_aposta": {
            "sena": exact_probability("megasena", 6),
            "quina": exact_probability("megasena", 5),
            "quadra": exact_probability("megasena", 4),
        },
        "cenario_monte_carlo": simulated,
        "aviso": ("Pesquisa sem apostas reais. Custos e faixas de prêmio são cenário "
                  "simplificado baseado em referência anterior. Lucro médio calculado "
                  "não é valor esperado real nem projeção de resultados futuros. "
                  "Eventos raros podem não aparecer nas simulações."),
    }


def main():
    panel = load_panel()
    report = build_report(panel)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    temp = DEST.with_suffix(".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    os.replace(temp, DEST)
    print("Simulação experimental Mega-Sena registrada:", DEST)
    print("Execuções:", report["cenario_monte_carlo"]["simulacoes"])


if __name__ == "__main__":
    main()
