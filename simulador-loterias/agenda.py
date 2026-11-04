"""Consulta oficial do próximo concurso e gera um painel JSON auditável."""
import datetime as dt
import json
import math
import os
import urllib.request
from pathlib import Path

from lottery import BASE, CONFIG, DATA, load

AGENDA = Path(__file__).parent / "data" / "painel.json"


def next_draw(payload):
    """Nunca inferir data/número/valor de concursos ainda não anunciados."""
    number = payload.get("numeroConcursoProximo")
    date = payload.get("dataProximoConcurso")
    estimate = payload.get("valorEstimadoProximoConcurso")
    if number is None or not date:
        raise ValueError("Caixa não informou próximo concurso completo")
    number = int(number)
    dt.datetime.strptime(str(date), "%d/%m/%Y")
    if number <= int(payload["numero"]):
        raise ValueError("Próximo concurso não é posterior ao último resultado")
    if estimate is not None:
        estimate = float(estimate)
        if not math.isfinite(estimate) or estimate < 0:
            raise ValueError("Estimativa inválida")
    return {"concurso": number, "data": str(date),
            "estimativa_premio": estimate, "estimativa_nao_garantida": True}


def build_panel(db, payloads, collected_at):
    panel = {"consultado_em_utc": collected_at, "modalidades": {}}
    for game in CONFIG:
        if not db.get(game):
            raise ValueError(f"Sem resultados armazenados: {game}")
        last_no = max(db[game], key=int)
        latest = db[game][last_no]
        remote = payloads[game]
        if int(remote["numero"]) != int(latest["numero"]):
            raise ValueError(
                f"Banco desatualizado para {game}: banco={latest['numero']} "
                f"Caixa={remote['numero']}; rodar coleta antes do painel"
            )
        panel["modalidades"][game] = {
            "ultimo_resultado": latest,
            "proximo_sorteio": next_draw(remote),
            "fonte": f"{BASE}/{game}",
            "historico_concursos": len(db[game]),
        }
    return panel


def update_panel():
    db = load()
    payloads = {}
    for game in CONFIG:
        url = f"{BASE}/{game}"
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 LoteriasResearch/1.0",
                          "Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=25) as response:
            payloads[game] = json.load(response)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    panel = build_panel(db, payloads, timestamp)
    AGENDA.parent.mkdir(parents=True, exist_ok=True)
    temp = AGENDA.with_suffix(".tmp")
    temp.write_text(json.dumps(panel, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
                    encoding="utf-8")
    os.replace(temp, AGENDA)
    print("Painel atualizado em", timestamp)
    for game, row in panel["modalidades"].items():
        print(f"{game}: resultado #{row['ultimo_resultado']['numero']} "
              f"-> próximo #{row['proximo_sorteio']['concurso']} "
              f"({row['proximo_sorteio']['data']}); "
              f"estimativa R$ {row['proximo_sorteio']['estimativa_premio']}")


if __name__ == "__main__":
    update_panel()
