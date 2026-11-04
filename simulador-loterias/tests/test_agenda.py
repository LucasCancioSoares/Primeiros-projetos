import unittest
from agenda import build_panel, next_draw


class AgendaTests(unittest.TestCase):
    def test_next_draw(self):
        p = {"numero": 30, "numeroConcursoProximo": 31,
             "dataProximoConcurso": "05/11/2026",
             "valorEstimadoProximoConcurso": 2500000}
        out = next_draw(p)
        self.assertEqual(out["concurso"], 31)
        self.assertTrue(out["estimativa_nao_garantida"])

    def test_reject_outdated_database(self):
        db = {g: {"20": {"numero": 20, "dezenas": []}} for g in
              ["lotofacil", "quina", "megasena"]}
        remotes = {g: {"numero": 21, "numeroConcursoProximo": 22,
                       "dataProximoConcurso": "06/11/2026"}
                   for g in db}
        with self.assertRaises(ValueError):
            build_panel(db, remotes, "2026-11-04T20:00:00Z")

    def test_reject_missing_next_date(self):
        with self.assertRaises(ValueError):
            next_draw({"numero": 20, "numeroConcursoProximo": 21})

    def test_reject_non_future(self):
        with self.assertRaises(ValueError):
            next_draw({"numero": 21, "numeroConcursoProximo": 21,
                       "dataProximoConcurso": "05/11/2026"})


if __name__ == "__main__":
    unittest.main()
