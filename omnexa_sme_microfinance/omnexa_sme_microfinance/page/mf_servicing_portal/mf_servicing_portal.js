frappe.pages["mf-servicing-portal"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Microfinance Field Portal"), single_column: true });
	const $body = $(`<div class="p-4">
		<h4>${__("Field Officer Desk")}</h4>
		<p class="text-muted">${__("Group lending · collections · solidarity cycles")}</p>
		<button class="btn btn-primary btn-open-cases">${__("Open Microfinance Cases")}</button>
		<button class="btn btn-default ms-2 btn-demo-hub">${__("Finance Demo Hub")}</button>
	</div>`);
	$(page.body).append($body);
	$body.find(".btn-open-cases").on("click", () => frappe.set_route("List", "Microfinance Case"));
	$body.find(".btn-demo-hub").on("click", () => frappe.set_route("finance-demo-hub"));
};
