import unittest
from integration import historical_payouts, historical_report


class IntegrationTests(unittest.TestCase):
    def test_payouts_from_descriptions(self):
        row = {"rateio": [{"descricao": "4 acertos", "premio": 514.1},
                          {"descricao": "5 acertos", "premio": 38878.66}]}
        self.assertEqual(historical_payouts(row), {4: 514.1, 5: 38878.66})

    def test_historical_uses_distinct_prizes_per_draw(self):
        tickets = [[1, 2, 3, 4, 5, 6]]
        records = [
            {"numero": 1, "data": "01/01/2026", "dezenas": tickets[0],
             "rateio": [{"descricao": "6 acertos", "premio": 100}]},
            {"numero": 2, "data": "02/01/2026", "dezenas": tickets[0],
             "rateio": [{"descricao": "6 acertos", "premio": 200}]},
        ]
        r = historical_report("megasena", tickets, 6, records)
        self.assertEqual(r["custo_total_hipotetico"], 12)
        self.assertEqual(r["receita_total"], 300)
        self.assertEqual(r["lucro_total"], 288)

    def test_no_made_up_rewards(self):
        r = historical_report("quina", [[1, 2, 3, 4, 5]], 3,
                              [{"numero": 1, "data": "01/01/2026",
                                "dezenas": [1, 2, 3, 4, 5], "rateio": []}])
        self.assertEqual(r["lucro_total"], -3)


if __name__ == "__main__":
    unittest.main()
