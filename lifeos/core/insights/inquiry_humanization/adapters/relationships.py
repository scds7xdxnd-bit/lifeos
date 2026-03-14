from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="relationships",
    replacements=(("cadence", "rhythm"),),
    event_record_label_singular="interaction record",
    event_record_label_plural="interaction records",
)
