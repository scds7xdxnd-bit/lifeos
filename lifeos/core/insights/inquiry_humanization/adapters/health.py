from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="health",
    replacements=(("metric", "health measure"),),
    event_record_label_singular="health record",
    event_record_label_plural="health records",
)
