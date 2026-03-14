from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="calendar",
    replacements=(("scheduling", "calendar"),),
    event_record_label_singular="calendar event",
    event_record_label_plural="calendar events",
)
