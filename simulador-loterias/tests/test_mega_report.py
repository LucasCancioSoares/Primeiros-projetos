import unittest
from mega_report import build_report


class TestMegaReport(unittest.TestCase):
    def test_report_uses_observed_secondary_tiers_not_future_jackpot(self):
        panel = {"modalidades": {"megasena": {
            "ultimo_resultado": {"numero": 101, "data": "01/11/2026",
                "rateio": [{"descricao": "6 acertos", "premio": 0},
                           {"descricao": "5 acertos", "premio": 15000},
                           {"descricao": "4 acertos", "premio": 500}]},
            "proximo_sorteio": {"concurso": 102, "estimativa_premio": 80000000}
        }}}
        result = build_report(panel, trials=100, seed=2026)
        self.assertEqual(result["premios_hipoteticos_usados"], {4: 500, 5: 15000})
        self.assertEqual(result["proximo_concurso_informado"], 102)
        self.assertEqual(result["cenario_monte_carlo"]["simulacoes"], 100)
        self.assertGreater(result["probabilidades_exatas_por_aposta"]["sena"], 0)


if __name__ == "__main__":
    unittest.main()
