# Copyright (c) 2026, ErpGenEx
import frappe

from omnexa_sme_microfinance.engine.lifecycle import MicrofinanceCaseInput, evaluate_microfinance_lifecycle


@frappe.whitelist()
def evaluate_lifecycle(
	principal: str,
	term_months: int,
	member_count: int = 5,
	group_maturity_cycles: int = 0,
	collection_rate: str = "0.95",
) -> dict:
	from decimal import Decimal

	result = evaluate_microfinance_lifecycle(
		MicrofinanceCaseInput(
			principal=Decimal(str(principal)),
			term_months=int(term_months),
			member_count=int(member_count),
			group_maturity_cycles=int(group_maturity_cycles),
			collection_rate=Decimal(str(collection_rate)),
		)
	)
	return result.to_dict()
