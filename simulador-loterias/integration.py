"""Integra painel oficial, resultados históricos e simulações financeiras."""
import json
import re
import statistics
from pathlib import Path
from finance import validate_tickets
from lottery import CONFIG

ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "data" / "painel.json"
RESULTS = ROOT / "data" / "resultados.json"


def load_panel(path=PANEL):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload.get("modalidades"), dict):
        raise ValueError("Painel sem modalidades")
    return payload


def load_results(path=RESULTS):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Histórico inválido")
    return payload


def historical_payouts(record):
    """Usa descrição explícita da faixa; não assume que faixa 1 é sempre 6/15."""
    paid = {}
    for tier in record.get("rateio", []):
        match = re.search(r"(?<!\d)(\d+)\s+acertos?\b",
                          str(tier.get("descricao", "")), re.IGNORECASE)
        if match:
            hits = int(match.group(1))
            amount = float(tier["premio"])
            if amount < 0:
                raise ValueError("Prêmio negativo")
            paid[hits] = amount
    return paid


def historical_report(game, tickets, stake, records):
    """Backtest descritivo: aposta fixa aplicada a todos os concursos conhecidos.

    O custo informado é hipotético/constante, NÃO custo histórico por data.
    Valores rateados representam somente as premiações oficiais daquele concurso.
    """
    tickets = validate_tickets(game, tickets)
    if stake <= 0:
        raise ValueError("Custo inválido")
    if not records:
        raise ValueError("Nenhum concurso histórico para análise")
    total, drawn = CONFIG[game]
    results = []
    for record in sorted(records, key=lambda x: int(x["numero"])):
        draw = frozenset(int(x) for x in record["dezenas"])
        if len(draw) != drawn or min(draw) < 1 or max(draw) > total:
            raise ValueError("Dezenas históricas inválidas")
        prize_map = historical_payouts(record)
        revenue = sum(prize_map.get(len(t & draw), 0) for t in tickets)
        cost = len(tickets) * stake
        results.append({
            "concurso": int(record["numero"]), "data": record["data"],
            "receita": round(revenue, 2), "custo": round(cost, 2),
            "lucro": round(revenue-cost, 2),
        })
    values = [row["lucro"] for row in results]
    return {
        "jogo": game, "concursos": len(results), "apostas_por_concurso": len(tickets),
        "custo_informado_por_aposta": stake,
        "custo_total_hipotetico": round(sum(r["custo"] for r in results), 2),
        "receita_total": round(sum(r["receita"] for r in results), 2),
        "lucro_total": round(sum(values), 2),
        "lucro_medio_por_concurso": round(statistics.mean(values), 2),
        "frequencia_historica_lucro": sum(x > 0 for x in values) / len(values),
        "detalhes": results,
        "aviso": ("Retrospectiva ilustrativa. O custo foi fornecido manualmente "
                  "e não representa o custo vigente em cada sorteio. Frequências "
                  "históricas não são probabilidades futuras."),
    }
