# Copyright (c) 2026, ErpGenEx
import unittest


class TestMicrofinanceApp(unittest.TestCase):
	def test_gap_register_closed(self):
		from omnexa_sme_microfinance.mf_gap_register import get_gap_status

		gs = get_gap_status()
		self.assertEqual(gs["gaps_total"], 48)
		self.assertEqual(gs["gaps_open"], 0)

	def test_global_score(self):
		from omnexa_sme_microfinance.mf_global_benchmark import get_global_mf_score

		score = get_global_mf_score()
		self.assertGreaterEqual(score["weighted_score"], 4.85)
