# Copyright (c) 2026, ErpGenEx
"""Sync MicroCapital world-class stack (idempotent)."""

from __future__ import annotations

import frappe


def sync_mf_world_class() -> dict:
	from omnexa_sme_microfinance.mf_governance import sync_mf_governance
	from omnexa_sme_microfinance.mf_report import ensure_microfinance_portfolio_report

	out = {"governance": sync_mf_governance(), "report": ensure_microfinance_portfolio_report()}
	try:
		from omnexa_sme_microfinance.mf_maturity import get_maturity_scores

		out["maturity"] = get_maturity_scores()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "mf_maturity after sync")
	out["benchmark"] = frappe.get_attr("omnexa_sme_microfinance.mf_global_benchmark.get_global_mf_score")()
	return out
