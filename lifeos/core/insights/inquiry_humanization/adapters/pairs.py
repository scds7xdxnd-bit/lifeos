from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter

PAIR_ADAPTERS = {
    "finance__habits": HumanizationAdapter(
        key="finance__habits",
        replacements=(("the two selected areas showing up together", "money and habit activity showing up together"),),
    ),
    "projects__skills": HumanizationAdapter(
        key="projects__skills",
        replacements=(
            ("the two selected areas showing up together", "project work and skill practice showing up together"),
        ),
    ),
    "projects__calendar": HumanizationAdapter(
        key="projects__calendar",
        replacements=(
            ("the two selected areas showing up together", "project work and calendar activity showing up together"),
        ),
    ),
    "habits__health": HumanizationAdapter(
        key="habits__health",
        replacements=(("the two selected areas showing up together", "habit and health activity showing up together"),),
    ),
    "habits__journal": HumanizationAdapter(
        key="habits__journal",
        replacements=(
            ("the two selected areas showing up together", "habit and journal activity showing up together"),
        ),
    ),
    "journal__relationships": HumanizationAdapter(
        key="journal__relationships",
        replacements=(
            ("the two selected areas showing up together", "journal and relationship activity showing up together"),
        ),
    ),
}
