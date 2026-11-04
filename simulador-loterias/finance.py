"""Motor financeiro de carteiras: valores de prêmios e custos são informados, nunca previstos."""
import argparse
import itertools
import json
import math
import random
from lottery import CONFIG


def validate_tickets(game, tickets):
    total, draw_size = CONFIG[game]
    normalized = []
    for ticket in tickets:
        numbers = tuple(sorted(int(x) for x in ticket))
        if len(numbers) != draw_size or len(set(numbers)) != draw_size:
            raise ValueError("Cada aposta deve ser simples e ter dezenas únicas")
        if numbers[0] < 1 or numbers[-1] > total:
            raise ValueError("Dezena fora do intervalo da modalidade")
        normalized.append(frozenset(numbers))
    if not normalized or len(set(normalized)) != len(normalized):
        raise ValueError("Carteira vazia ou com apostas repetidas")
    return normalized


def evaluate(game, tickets, outcomes, stake, payouts):
    """Outcomes é uma sequência de sorteios, cada um com números e prêmios por faixa.
    payouts é um mapa acertos->valor hipotético ou cenário válido para o sorteio.
    Todos os tickets da carteira são avaliados contra o MESMO sorteio.
    """
    tickets = validate_tickets(game, tickets)
    if not math.isfinite(stake) or stake <= 0:
        raise ValueError("Custo por aposta deve ser positivo e finito")
    cost = len(tickets) * stake
    values = {}
    for hits, prize in payouts.items():
        h, p = int(hits), float(prize)
        if h < 0 or h > CONFIG[game][1] or not math.isfinite(p) or p < 0:
            raise ValueError("Premiação inválida")
        values[h] = p
    profits = []
    for outcome in outcomes:
        draw = set(int(x) for x in outcome)
        if len(draw) != CONFIG[game][1] or any(x < 1 or x > CONFIG[game][0] for x in draw):
            raise ValueError("Sorteio inválido")
        revenue = sum(values.get(len(t & draw), 0.0) for t in tickets)
        profits.append(revenue - cost)
    if not profits:
        raise ValueError("Necessário ao menos um sorteio")
    profits.sort()
    n = len(profits)
    return {
        "jogo": game, "apostas": len(tickets), "custo_por_concurso": round(cost, 2),
        "simulacoes": n, "lucro_medio": round(sum(profits) / n, 4),
        "lucro_mediano": round((profits[(n - 1)//2] + profits[n//2])/2, 4),
        "probabilidade_de_lucro": sum(x > 0 for x in profits)/n,
        "probabilidade_de_prejuizo": sum(x < 0 for x in profits)/n,
        "percentil_05_lucro": round(profits[int((n-1)*0.05)], 4),
        "lucro_minimo": round(profits[0], 4),
        "lucro_maximo": round(profits[-1], 4),
    }


def simulate_portfolio(game, tickets, stake, payouts, trials=10000, seed=2026):
    if not (1 <= trials <= 10_000_000):
        raise ValueError("Número de simulações inválido")
    universe, draw_size = CONFIG[game]
    rng = random.Random(seed)
    draws = (rng.sample(range(1, universe + 1), draw_size) for _ in range(trials))
    result = evaluate(game, tickets, draws, stake, payouts)
    result["semente"] = seed
    result["observacao"] = ("Premiações fixas são cenários hipotéticos; valores reais variam por "
                            "concurso. Não se trata de previsão ou garantia de lucro.")
    return result


def make_tickets(game, quantity, seed=2026):
    """Gera uma carteira distinta aleatória para referência, NÃO uma previsão."""
    universe, draw_size = CONFIG[game]
    if quantity < 1 or quantity > math.comb(universe, draw_size):
        raise ValueError("Quantidade inválida")
    rng = random.Random(seed)
    result = set()
    while len(result) < quantity:
        result.add(tuple(sorted(rng.sample(range(1, universe + 1), draw_size))))
    return sorted(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulação experimental de carteira")
    parser.add_argument("--game", choices=CONFIG, default="lotofacil")
    parser.add_argument("--quantity", type=int, default=5)
    parser.add_argument("--stake", type=float, required=True)
    parser.add_argument("--payouts", required=True, help='JSON por acertos, ex: {"11":7,"12":14}')
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    tickets = make_tickets(args.game, args.quantity, args.seed)
    print(json.dumps(simulate_portfolio(args.game, tickets, args.stake,
                                        json.loads(args.payouts), args.trials, args.seed),
                     ensure_ascii=False, indent=2))
