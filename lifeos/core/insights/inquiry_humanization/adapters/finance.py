from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="finance",
    replacements=(("ledger", "money record"), ("cashflow", "money flow"), ("cash flow", "money flow")),
    event_record_label_singular="transaction record",
    event_record_label_plural="transaction records",
)
