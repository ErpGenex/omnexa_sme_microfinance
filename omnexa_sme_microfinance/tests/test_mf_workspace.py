# Copyright (c) 2026, ErpGenEx
import unittest

import frappe


class TestMicrofinanceWorkspace(unittest.TestCase):
	def test_workspace_has_links(self):
		from omnexa_sme_microfinance.workspace.mf_workspace import sync_mf_workspace

		sync_mf_workspace()
		frappe.db.commit()
		links = frappe.db.count(
			"Workspace Link", {"parent": "SME Microfinance", "parenttype": "Workspace"}
		)
		self.assertGreaterEqual(links, 25, f"SME Microfinance workspace links={links}")

	def test_microfinance_case_list_route(self):
		self.assertTrue(frappe.db.exists("DocType", "Microfinance Case"))
