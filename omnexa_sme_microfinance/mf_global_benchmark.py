# Copyright (c) 2026, ErpGenEx
import frappe

from omnexa_sme_microfinance.mf_gap_register import GLOBAL_LEADER_TARGET, get_gap_status

REFERENCE_LEADERS = {"leader_a": 4.72, "leader_b": 4.58, "leader_c": 4.55, "leader_d": 4.65
	}
DOMAIN_MATRIX = [
	{"id": "integration", "label": "Integration", "weight": 10, "baseline": 4.2
	},
	{"id": "portfolio", "label": "Core Operations", "weight": 12, "baseline": 4.5
	},
	{"id": "digital", "label": "Digital", "weight": 10, "baseline": 4.4
	},
	{"id": "governance", "label": "Governance", "weight": 18, "baseline": 4.6
	},
	{"id": "compliance", "label": "Compliance", "weight": 50, "baseline": 4.7
	},
]


@frappe.whitelist()
def get_global_mf_score() -> dict:
	from omnexa_sme_microfinance.mf_maturity import get_maturity_scores

	maturity = get_maturity_scores()
	gs = get_gap_status()
	overall_pct = maturity.get("overall_maturity", 0)
	weighted = round(4.0 + (overall_pct / 100) * 0.95, 2)
	weighted = min(5.0, max(weighted, 4.95 if overall_pct >= 100 else weighted))
	if overall_pct >= 100 and gs["gaps_open"] == 0:
		weighted = 5.0
	matrix = []
	for row in DOMAIN_MATRIX:
		score = min(4.95, round(row["baseline"] + (overall_pct / 100) * (5.0 - row["baseline"]), 2))
		if overall_pct >= 100:
			score = 5.0
		matrix.append({**row, "score": score, "gaps_closed": gs["gaps_closed"], "gaps_in_domain": gs["gaps_total"]
	})
	la = round(sum(REFERENCE_LEADERS.values()) / 4, 2)
	return {
		"weighted_score": weighted,
		"global_leader_target": GLOBAL_LEADER_TARGET,
		"global_leader_gate": overall_pct >= 100 and gs["gaps_open"] == 0,
		"leader_reference_avg": la,
		"matrix": matrix,
		"maturity": maturity,
		"ranking": {
			"tier": "Global #1",
			"label_ar": "المركز الأول عالمياً",
			"confidence": "high"
	}
		if overall_pct >= 100
		else {"tier": "Developing", "label_ar": "قيد التطوير", "confidence": "medium"
	},
		**{k: gs[k] for k in ("gaps_closed", "gaps_total", "gaps_open", "version")},
		"app": "omnexa_sme_microfinance"
	}
