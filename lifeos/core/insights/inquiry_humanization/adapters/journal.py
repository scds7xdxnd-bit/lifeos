from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

ADAPTER = HumanizationAdapter(
    key="journal",
    replacements=(("reflection", "journal reflection"),),
    event_record_label_singular="journal entry",
    event_record_label_plural="journal entries",
)
