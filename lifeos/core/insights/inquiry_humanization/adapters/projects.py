from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="projects",
    replacements=(("throughput", "completed work"), ("slippage", "delay")),
    event_record_label_singular="project record",
    event_record_label_plural="project records",
)
