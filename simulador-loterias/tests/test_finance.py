import unittest
from finance import evaluate, make_tickets, simulate_portfolio


class TestFinance(unittest.TestCase):
    def test_all_tickets_share_one_draw(self):
        # Carteira de 2 apostas da Mega-Sena, segundo ticket é premiado com 6 acertos
        a = [1, 2, 3, 4, 5, 6]
        b = [7, 8, 9, 10, 11, 12]
        report = evaluate("megasena", [a, b], [b], 6.0, {6: 100.0})
        self.assertEqual(report["custo_por_concurso"], 12)
        self.assertEqual(report["lucro_medio"], 88)
        self.assertEqual(report["probabilidade_de_lucro"], 1)

    def test_invalid_duplicates(self):
        with self.assertRaises(ValueError):
            evaluate("quina", [[1, 2, 3, 4, 5]] * 2,
                     [[1, 2, 3, 4, 5]], 3, {5: 1})

    def test_no_prize_is_loss(self):
        report = simulate_portfolio("megasena", [[1,2,3,4,5,6]], 6,
                                    {}, trials=50, seed=1)
        self.assertEqual(report["lucro_medio"], -6)
        self.assertEqual(report["probabilidade_de_prejuizo"], 1)

    def test_reproducibility(self):
        tickets = make_tickets("lotofacil", 3, 33)
        a = simulate_portfolio("lotofacil", tickets, 3.5, {11: 7}, 200, 9)
        b = simulate_portfolio("lotofacil", tickets, 3.5, {11: 7}, 200, 9)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
