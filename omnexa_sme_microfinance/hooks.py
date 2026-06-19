app_name = "omnexa_sme_microfinance"
app_title = "ErpGenEx — SME Microfinance"
app_publisher = "ErpGenEx"
app_description = "Micro-SME and group lending finance vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

required_apps = ["omnexa_core"]

after_migrate = ["omnexa_sme_microfinance.workspace.mf_workspace.sync_mf_workspace"]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Omnexa SME Microfinance"]],
	},
]
