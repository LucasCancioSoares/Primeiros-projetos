import math
import unittest
from lottery import CONFIG, exact_probability, validate

class TestLottery(unittest.TestCase):
    def test_probabilities_sum_one(self):
        for game, (_, drawn) in CONFIG.items():
            self.assertAlmostEqual(sum(exact_probability(game, h)
                                       for h in range(drawn + 1)), 1.0, places=10)

    def test_main_prize(self):
        self.assertAlmostEqual(exact_probability("megasena", 6),
                               1 / math.comb(60, 6))

    def test_validate(self):
        record = {"numero": 9, "listaDezenas": list(map(str, range(1, 16))),
                  "dataApuracao": "01/01/2026", "listaRateioPremio": []}
        self.assertEqual(validate("lotofacil", record)["numero"], 9)
        record["listaDezenas"][0] = "02"
        with self.assertRaises(ValueError):
            validate("lotofacil", record)

if __name__ == "__main__":
    unittest.main()
