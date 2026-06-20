# Copyright (c) 2026, ErpGenEx
"""Post-migrate: KPI charts (control tower) + full sidebar links."""

from __future__ import annotations

import os

import frappe
from frappe.modules.import_file import import_file_by_path

_APP = "omnexa_sme_microfinance"


def _ensure_pages() -> None:
	page_root = frappe.get_app_path(_APP, "omnexa_sme_microfinance", "page")
	if not os.path.isdir(page_root):
		return
	for folder in sorted(os.listdir(page_root)):
		json_path = os.path.join(page_root, folder, f"{folder}.json")
		if os.path.isfile(json_path):
			import_file_by_path(json_path, force=True)


def after_migrate() -> None:
	try:
		_ensure_pages()
		from omnexa_sme_microfinance.workspace.mf_workspace import sync_mf_workspace

		sync_mf_workspace()
		from omnexa_sme_microfinance.mf_world_class import sync_mf_world_class

		sync_mf_world_class()
		frappe.db.commit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"{_APP}: workspace_enhancer")
