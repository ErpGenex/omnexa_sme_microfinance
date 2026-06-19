frappe.pages["mf-executive-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Microfinance Executive"), single_column: true });
	frappe.call({
		method: "omnexa_sme_microfinance.mf_global_benchmark.get_global_mf_score",
		callback(r) {
			const s = r.message || {};
			$(page.body).html(
				`<div class="p-4"><h4>MicroCapital Score: <b>${s.weighted_score || 0}</b></h4>
				<p>${s.gaps_closed || 0} / ${s.gaps_total || 48} gaps</p>
				<p>${s.ranking?.label_ar || ""}</p></div>`
			);
		},
	});
};
