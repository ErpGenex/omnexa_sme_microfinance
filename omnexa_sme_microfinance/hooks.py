app_name = "omnexa_sme_microfinance"
app_title = "ErpGenEx — SME Microfinance"
app_publisher = "ErpGenEx"
app_description = "Micro-SME and group lending finance vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

required_apps = ["omnexa_core"]

doc_events = {
	"Microfinance Case": {
		"before_workflow_action": "omnexa_sme_microfinance.omnexa_sme_microfinance.doctype.microfinance_case.microfinance_case.before_workflow_action",
	},
}

add_to_apps_screen = [
	{
		"name": "omnexa_sme_microfinance",
		"logo": "/assets/omnexa_sme_microfinance/logo.png",
		"title": "MicroCapital",
		"route": "/app/mf-servicing-portal",
	}
]


after_migrate = ["omnexa_sme_microfinance.workspace_enhancer.after_migrate"]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Omnexa SME Microfinance"]],
	},
]
