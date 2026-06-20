# Copyright (c) 2026, ErpGenEx
import unittest

import frappe


class TestMFMaturity(unittest.TestCase):
	def test_maturity_scores_after_sync(self):
		from omnexa_sme_microfinance.mf_world_class import sync_mf_world_class

		sync_mf_world_class()
		frappe.db.commit()
		from omnexa_sme_microfinance.mf_maturity import get_maturity_scores

		scores = get_maturity_scores()
		self.assertGreaterEqual(scores["overall_maturity"], 95)
		for key in (
			"process_excellence",
			"governance",
			"compliance",
			"automation",
			"world_ranking_readiness",
		):
			self.assertGreaterEqual(scores[key], 95, msg=key)

	def test_global_benchmark_gate(self):
		from omnexa_sme_microfinance.mf_global_benchmark import get_global_mf_score

		result = get_global_mf_score()
		self.assertGreaterEqual(result["maturity"]["overall_maturity"], 95)
