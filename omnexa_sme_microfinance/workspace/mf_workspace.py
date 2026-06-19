# Copyright (c) 2026, ErpGenEx
"""SME Microfinance workspace sync."""

from __future__ import annotations

import frappe


def sync_mf_workspace() -> str:
	from omnexa_core.omnexa_core.workspace_control_tower import sync_workspace_for_app

	return sync_workspace_for_app("omnexa_sme_microfinance") or "SME Microfinance"
