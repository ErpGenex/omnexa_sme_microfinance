# Copyright (c) 2026, ErpGenEx
"""Microfinance group-lending lifecycle engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MicrofinanceCaseInput:
	principal: Decimal
	term_months: int
	member_count: int = 5
	group_maturity_cycles: int = 0
	collection_rate: Decimal = Decimal("0.95")


@dataclass(frozen=True)
class MicrofinanceLifecycleResult:
	risk_score: Decimal
	recommended_stage: str
	risk_band: str
	group_limit: Decimal
	collection_priority: str
	reason_codes: list[str]
	required_controls: list[str]

	def to_dict(self) -> dict:
		return {
			"risk_score": str(self.risk_score),
			"recommended_stage": self.recommended_stage,
			"risk_band": self.risk_band,
			"group_limit": str(self.group_limit),
			"collection_priority": self.collection_priority,
			"reason_codes": self.reason_codes,
			"required_controls": self.required_controls,
		}


def evaluate_microfinance_lifecycle(c: MicrofinanceCaseInput) -> MicrofinanceLifecycleResult:
	risk = Decimal("0.05")
	reasons: list[str] = []
	controls = ["GROUP_KYC", "SOLIDARITY_GUARANTEE", "FIELD_VERIFICATION"]

	if c.member_count < 3:
		risk += Decimal("0.06")
		reasons.append("SMALL_GROUP_SIZE")
		controls.append("GROUP_SIZE_REVIEW")
	elif c.member_count > 15:
		risk += Decimal("0.03")
		reasons.append("LARGE_GROUP_COMPLEXITY")

	if c.group_maturity_cycles < 1:
		risk += Decimal("0.05")
		reasons.append("NEW_GROUP")
		controls.append("MENTOR_GROUP_LINK")
	else:
		risk -= Decimal("0.02")

	if c.collection_rate < Decimal("0.85"):
		risk += Decimal("0.08")
		reasons.append("WEAK_COLLECTION_HISTORY")
		controls.append("INTENSIVE_FIELD_MONITORING")

	per_member = c.principal / max(c.member_count, 1)
	if per_member > Decimal("15000"):
		risk += Decimal("0.04")
		reasons.append("HIGH_PER_MEMBER_EXPOSURE")

	risk = max(Decimal("0.01"), min(Decimal("0.35"), risk))
	if risk <= Decimal("0.10"):
		band, stage, priority = "A", "Disbursement", "Standard"
	elif risk <= Decimal("0.16"):
		band, stage, priority = "B", "Disbursement", "Standard"
	elif risk <= Decimal("0.22"):
		band, stage, priority = "C", "Collection", "Elevated"
	else:
		band, stage, priority = "D", "Origination", "Intensive"

	limit = (c.principal * (Decimal("1") + (Decimal("0.15") - risk))).quantize(Decimal("0.01"))
	return MicrofinanceLifecycleResult(
		risk_score=risk,
		recommended_stage=stage,
		risk_band=band,
		group_limit=limit,
		collection_priority=priority,
		reason_codes=reasons or ["SOLIDARITY_GROUP_OK"],
		required_controls=controls,
	)
