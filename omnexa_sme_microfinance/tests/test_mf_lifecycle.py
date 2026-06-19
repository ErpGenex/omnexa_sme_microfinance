# Copyright (c) 2026, ErpGenEx
import unittest
from decimal import Decimal


class TestMicrofinanceLifecycle(unittest.TestCase):
	def test_group_lending_lifecycle(self):
		from omnexa_sme_microfinance.engine.lifecycle import MicrofinanceCaseInput, evaluate_microfinance_lifecycle

		result = evaluate_microfinance_lifecycle(
			MicrofinanceCaseInput(principal=Decimal("50000"), term_months=12, member_count=8, group_maturity_cycles=2)
		)
		self.assertIn(result.risk_band, ("A", "B", "C", "D"))
		self.assertTrue(result.reason_codes)
