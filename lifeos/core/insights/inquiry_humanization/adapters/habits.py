from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="habits",
    replacements=(("streak", "run of logged days"), ("adherence", "follow-through")),
    event_record_label_singular="habit log",
    event_record_label_plural="habit logs",
)
