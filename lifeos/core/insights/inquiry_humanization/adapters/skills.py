from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="skills",
    replacements=(("practice cadence", "practice rhythm"), ("progression", "progress pattern")),
    event_record_label_singular="practice log",
    event_record_label_plural="practice logs",
)
