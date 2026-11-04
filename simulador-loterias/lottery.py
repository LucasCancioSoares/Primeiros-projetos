"""Coletor e simulador experimental, sem promessa de previsibilidade."""
import argparse
import datetime as dt
import json
import math
import os
import random
import time
import urllib.request
from pathlib import Path

BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api"
CONFIG = {
    "lotofacil": (25, 15),
    "quina": (80, 5),
    "megasena": (60, 6),
}
DATA = Path(__file__).parent / "data" / "resultados.json"


def validate(game, item):
    universe, count = CONFIG[game]
    number = int(item["numero"])
    raw = item["listaDezenas"]
    if not isinstance(raw, list):
        raise ValueError("Dezenas ausentes")
    balls = sorted(int(n) for n in raw)
    if len(balls) != count or len(set(balls)) != count:
        raise ValueError(f"Quantidade/duplicacao invalida em {game} #{number}")
    if balls[0] < 1 or balls[-1] > universe:
        raise ValueError("Dezena fora da faixa")
    date = str(item["dataApuracao"])
    dt.datetime.strptime(date, "%d/%m/%Y")
    ranges = []
    for row in item.get("listaRateioPremio", []):
        ranges.append({
            "faixa": int(row["faixa"]),
            "ganhadores": int(row["numeroDeGanhadores"]),
            "premio": float(row["valorPremio"]),
            "descricao": str(row.get("descricaoFaixa", "")),
        })
    return {
        "numero": number, "data": date, "dezenas": balls,
        "rateio": ranges, "acumulado": bool(item.get("acumulado", False)),
        "fonte": f"{BASE}/{game}/{number}",
    }


def fetch(game, number=None, retries=3):
    url = f"{BASE}/{game}" + (f"/{number}" if number else "")
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 LoteriasResearch/1.0",
                              "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=25) as response:
                return validate(game, json.load(response))
        except (OSError, ValueError, KeyError, TypeError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def load():
    if not DATA.exists():
        return {game: {} for game in CONFIG}
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    return {game: payload.get(game, {}) for game in CONFIG}


def update(backfill=0):
    db = load()
    errors = []
    for game in CONFIG:
        try:
            last = fetch(game)
            latest = last["numero"]
            known = max((int(n) for n in db[game]), default=0)
            if known:
                numbers = range(known + 1, latest + 1)
            elif backfill:
                numbers = range(max(1, latest - backfill + 1), latest + 1)
            else:
                numbers = [latest]
            for n in numbers:
                try:
                    item = last if n == latest else fetch(game, n)
                    db[game][str(n)] = item
                except Exception as exc:
                    errors.append(f"{game} #{n}: {exc}")
                time.sleep(0.25)
            print(f"{game}: ultimo concurso {latest}; registros {len(db[game])}")
        except Exception as exc:
            errors.append(f"{game}: {exc}")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    os.replace(tmp, DATA)
    if errors:
        raise RuntimeError("Coleta incompleta: " + "; ".join(errors))


def exact_probability(game, hits):
    universe, drawn = CONFIG[game]
    if hits < 0 or hits > drawn:
        return 0.0
    return (math.comb(drawn, hits) * math.comb(universe - drawn, drawn - hits)
            / math.comb(universe, drawn)
            if 0 <= drawn - hits <= universe - drawn else 0.0)


def monte_carlo(game, trials=100000, seed=2026):
    universe, drawn = CONFIG[game]
    rng = random.Random(seed)
    ticket = set(range(1, drawn + 1))
    counts = {h: 0 for h in range(drawn + 1)}
    for _ in range(trials):
        result = set(rng.sample(range(1, universe + 1), drawn))
        counts[len(ticket & result)] += 1
    print(f"Jogo: {game}; simulacoes: {trials}; semente: {seed}")
    for hits, occurrences in counts.items():
        if occurrences:
            print(f"{hits} acertos: simulado={occurrences/trials:.8f} "
                  f"teorico={exact_probability(game, hits):.8f}")
    print("Aviso: dados passados nao tornam os proximos sorteios previsiveis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["update", "simulate"])
    parser.add_argument("--game", choices=list(CONFIG), default="lotofacil")
    parser.add_argument("--trials", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--backfill", type=int, default=0)
    args = parser.parse_args()
    if args.command == "update":
        update(backfill=args.backfill)
    else:
        if args.trials <= 0 or args.trials > 10000000:
            parser.error("--trials deve estar entre 1 e 10000000")
        monte_carlo(args.game, args.trials, args.seed)
