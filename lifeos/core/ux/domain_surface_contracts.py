"""Domain surface definitions for Phase 3a.5 (backend structure only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class SurfaceSection:
    name: str
    editable: bool
    edit_entry: Optional[str] = None
    requires_confirmation: bool = False


@dataclass(frozen=True)
class SurfaceField:
    label: str
    meaning: str
    source: str  # user_entered | system_derived | imported
    stability: str  # stable | likely_to_change


@dataclass(frozen=True)
class DomainSurfaceDefinition:
    domain: str
    surface_name: str
    purpose: str
    primary_question: str
    primary_action: Optional[str]
    read_only_sections: List[SurfaceSection]
    editable_sections: List[SurfaceSection]
    confidence_rules: List[str]
    insight_contracts: List[str]
    data_fields: List[SurfaceField]
    tier: int


DOMAIN_SURFACE_CONTRACTS: dict[str, DomainSurfaceDefinition] = {
    # Tier 0: Profile (read-only surface)
    "profile:settings": DomainSurfaceDefinition(
        domain="profile",
        surface_name="Profile",
        purpose="Provide a calm, read-first view of account safety, session posture, and configuration state.",
        primary_question="Is my account safe and configured?",
        primary_action=None,
        read_only_sections=[
            SurfaceSection(name="Session summary", editable=False),
            SurfaceSection(name="Role summary", editable=False),
            SurfaceSection(name="Security status", editable=False),
        ],
        editable_sections=[],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Account status", meaning="Current account status", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Active sessions count",
                meaning="Count of active sessions",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Role summary", meaning="User role summary", source="system_derived", stability="stable"
            ),
        ],
        tier=0,
    ),
    # Tier 0: Journal
    "journal:entries": DomainSurfaceDefinition(
        domain="journal",
        surface_name="Journal",
        purpose="Provide a calm record of recent notes and reflections without forcing action.",
        primary_question="What did I note and how did I feel?",
        primary_action="Review recent entries",
        read_only_sections=[
            SurfaceSection(name="Recent entries list", editable=False),
            SurfaceSection(name="Mood/tags summary", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="New entry creation", editable=True, edit_entry="New entry", requires_confirmation=False
            ),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Entry text", meaning="User-authored reflection", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Tags/mood", meaning="User-described tags or mood", source="user_entered", stability="stable"
            ),
            SurfaceField(label="Timestamp", meaning="Entry timestamp", source="system_derived", stability="stable"),
        ],
        tier=0,
    ),
    # Tier 0: Focused Inquiry
    "insights:inquiry": DomainSurfaceDefinition(
        domain="insights",
        surface_name="Focused Inquiry",
        purpose="Provide one deterministic evidence-based brief for a scoped user question.",
        primary_question="What exactly am I trying to understand right now?",
        primary_action="Generate brief",
        read_only_sections=[
            SurfaceSection(name="Inquiry brief findings", editable=False),
            SurfaceSection(name="Evidence references", editable=False),
            SurfaceSection(name="Inquiry history", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="Inquiry scope form",
                editable=True,
                edit_entry="Generate brief",
                requires_confirmation=True,
            ),
            SurfaceSection(
                name="Refine scope",
                editable=True,
                edit_entry="Refine inquiry",
                requires_confirmation=True,
            ),
        ],
        confidence_rules=["informational", "needs_review", "confirmed"],
        insight_contracts=[
            "focused_inquiry_domain_brief",
            "focused_inquiry_cross_domain_brief",
            "focused_inquiry_timeline_domain_brief",
            "focused_inquiry_timeline_cross_domain_brief",
        ],
        data_fields=[
            SurfaceField(
                label="Response ok", meaning="Response success flag", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response deduped", meaning="Create dedupe indicator", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response inquiry id", meaning="Inquiry identifier", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response version id",
                meaning="Brief version identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response version number",
                meaning="Brief version number",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response inquiry",
                meaning="Inquiry payload container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response items", meaning="Inquiry list payload", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response total", meaning="Inquiry list total count", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response limit", meaning="Inquiry list limit", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response offset", meaning="Inquiry list offset", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response latest brief",
                meaning="Latest brief payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response brief", meaning="Refine brief payload", source="system_derived", stability="stable"
            ),
            SurfaceField(label="Inquiry id", meaning="Inquiry id", source="system_derived", stability="stable"),
            SurfaceField(
                label="Question", meaning="Scoped inquiry question", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Lens", meaning="Domain or cross-domain inquiry lens", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Primary domain", meaning="Primary selected domain", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Selected domains",
                meaning="Explicit selected domain list",
                source="user_entered",
                stability="stable",
            ),
            SurfaceField(
                label="Timeframe object", meaning="Timeframe object", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Timeframe start", meaning="Timeframe start timestamp", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Timeframe end", meaning="Timeframe end timestamp", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="As of timestamp",
                meaning="Deterministic as_of timestamp",
                source="user_entered",
                stability="stable",
            ),
            SurfaceField(
                label="Context block",
                meaning="User context block labeled non-evidence",
                source="user_entered",
                stability="stable",
            ),
            SurfaceField(
                label="Context label", meaning="Context block label", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Context note", meaning="Context block note", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Created timestamp",
                meaning="Inquiry created timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Updated timestamp",
                meaning="Inquiry updated timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Last version number",
                meaning="Latest brief version number",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Latest brief object",
                meaning="Latest brief version object",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Version history list", meaning="All brief versions", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief version id",
                meaning="Brief version identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief version number",
                meaning="Brief version number",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Parent version id",
                meaning="Previous brief version link",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief created timestamp",
                meaning="Brief version creation timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief hash", meaning="Brief deterministic hash", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief as of timestamp",
                meaning="Brief as_of timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief payload", meaning="Inquiry brief payload", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief summary", meaning="Inquiry brief summary", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief findings", meaning="Inquiry brief findings", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief direct answer",
                meaning="Deterministic direct answer block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief answerability block",
                meaning="Deterministic answerability classification block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief context non evidence",
                meaning="Context section marked non-evidence",
                source="user_entered",
                stability="stable",
            ),
            SurfaceField(
                label="Brief uncertainty note",
                meaning="Inquiry-level uncertainty note",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief limits", meaning="Inquiry limits list", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Brief limitation items",
                meaning="Canonical limitation item list",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief refine guidance",
                meaning="Productized refine guidance list",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief bounded patterns",
                meaning="Bounded pattern synthesis list",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief productization metadata",
                meaning="Productization stage metadata block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief generated timestamp",
                meaning="Brief generated timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief profile metadata",
                meaning="Domain expert/generic brief profile metadata",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief profile key",
                meaning="Brief profile identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief profile version",
                meaning="Brief profile version",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief strategy key",
                meaning="Strategy identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief strategy version",
                meaning="Strategy version identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief profile domain",
                meaning="Domain scope for brief profile",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief expert mode",
                meaning="Whether domain expert strategy mode was used",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief finding categories",
                meaning="Finding category list emitted by strategy",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief timeline metadata",
                meaning="Deterministic timeline metadata for replay and window coverage",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief humanized rendering",
                meaning="Deterministic derived humanized brief rendering",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Brief quality metadata",
                meaning="Deterministic brief quality metadata",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality findings total",
                meaning="Quality findings total",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality findings with evidence",
                meaning="Quality findings with canonical evidence",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality evidence coverage ratio",
                meaning="Quality evidence coverage ratio",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality structure gaps",
                meaning="Deterministic structural quality gaps",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality sparse domains",
                meaning="Domains with sparse observed evidence coverage",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Quality refine guidance",
                meaning="Deterministic refinement guidance from quality evaluation",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Canonical finding id",
                meaning="Stable canonical finding traceability identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding claim", meaning="Finding claim text", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Finding category",
                meaning="Domain finding category",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding evidence refs",
                meaning="Finding evidence references",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding relevance rank",
                meaning="Deterministic relevance rank",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding relevance reason",
                meaning="Deterministic relevance explanation",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding confidence label",
                meaning="Finding confidence label",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding uncertainty note",
                meaning="Finding uncertainty note",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding source domains",
                meaning="Finding source domain labels",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Finding timeline context",
                meaning="Timeline comparison context for a finding",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Canonical limitation id",
                meaning="Stable canonical limitation traceability identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Limitation text",
                meaning="Canonical limitation text",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence source kind",
                meaning="Evidence source type",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence source id",
                meaning="Evidence source record id",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence source ref",
                meaning="Evidence source reference key",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence event type",
                meaning="Evidence source event type",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence domain", meaning="Evidence source domain", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Evidence created at",
                meaning="Evidence source timestamp",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence event count",
                meaning="Read-model event count evidence",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Evidence insight count",
                meaning="Read-model insight count evidence",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Direct answer text",
                meaning="Direct answer text",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Direct answer supporting claims",
                meaning="Direct answer supporting claims",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Direct answer note",
                meaning="Direct answer scope note",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Answerability classification",
                meaning="Answerability classification",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Answerability reason",
                meaning="Answerability reasoning note",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Answerability evidence coverage ratio",
                meaning="Answerability evidence coverage ratio",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Answerability supporting finding count",
                meaning="Answerability supporting finding count",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Bounded pattern category",
                meaning="Bounded pattern category",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Bounded pattern finding count",
                meaning="Bounded pattern finding count",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Bounded pattern note",
                meaning="Bounded pattern note",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Productization version",
                meaning="Productization layer version",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Limitations before dedupe",
                meaning="Limitation count before deduplication",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Limitations after dedupe",
                meaning="Limitation count after deduplication",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Removed duplicate limitations",
                meaning="Removed duplicate limitation count",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Direct answer presence",
                meaning="Direct answer presence flag",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline claim type",
                meaning="Timeline claim class",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline active window label",
                meaning="Active comparable window label",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline comparison label",
                meaning="Timeline comparison reference label",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline window spec token",
                meaning="Timeline window specification token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline baseline policy token",
                meaning="Timeline baseline policy token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline coverage status",
                meaning="Timeline coverage status for finding-level interpretation",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline profile id",
                meaning="Timeline profile identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline profile version",
                meaning="Timeline profile version",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline engine version",
                meaning="Timeline engine version",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline metadata window spec token",
                meaning="Timeline metadata window specification token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline active window token",
                meaning="Deterministic active window identity token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline comparison window token",
                meaning="Deterministic comparison window identity token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline metadata baseline policy token",
                meaning="Timeline metadata baseline policy token",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline timezone token",
                meaning="Captured timezone token for timeline computation",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline metadata as of timestamp",
                meaning="Timeline as_of timestamp used for replay identity",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline evidence manifest hash",
                meaning="Timeline evidence manifest hash",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline summary hash",
                meaning="Timeline summary hash",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline comparison coverage",
                meaning="Timeline comparison coverage block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline finding count",
                meaning="Number of timeline findings in the brief",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline insufficiency count",
                meaning="Timeline insufficiency count",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline prior window availability",
                meaning="Whether prior comparable window exists",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline baseline windows available",
                meaning="Available baseline windows",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline baseline windows required",
                meaning="Required baseline windows",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline recurrence windows available",
                meaning="Comparable windows available for recurrence",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Timeline trend windows available",
                meaning="Comparable windows available for trend",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized canonical brief hash",
                meaning="Canonical brief hash used to derive the humanized brief",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanization version",
                meaning="Deterministic humanization layer version",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized brief hash",
                meaning="Deterministic humanized brief hash",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Technical view available",
                meaning="Whether the canonical technical brief remains available alongside the humanized view",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized answer text",
                meaning="Default humanized answer text",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized answer source finding ids",
                meaning="Canonical finding ids supporting the humanized answer",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized answer source limitation ids",
                meaning="Canonical limitation ids supporting the humanized answer",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block id",
                meaning="Humanized block identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block text",
                meaning="Humanized block text",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block source finding ids",
                meaning="Canonical finding ids linked to a humanized block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block source limitation ids",
                meaning="Canonical limitation ids linked to a humanized block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block evidence refs",
                meaning="Evidence refs exposed on a humanized block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized block confidence label",
                meaning="Canonical confidence label preserved on a humanized block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized section id",
                meaning="Humanized section identifier",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized section title",
                meaning="Humanized section title",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized section blocks",
                meaning="Humanized section block list",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized brief metadata",
                meaning="Humanized brief replay metadata",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized brief answer",
                meaning="Humanized brief answer block",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Humanized brief sections",
                meaning="Humanized brief section list",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=0,
    ),
    # Tier 1: Projects
    "projects:dashboard": DomainSurfaceDefinition(
        domain="projects",
        surface_name="Projects Dashboard",
        purpose="Surface active projects and the next meaningful step without exposing full task tables by default.",
        primary_question="What is the next meaningful step?",
        primary_action="Review projects",
        read_only_sections=[
            SurfaceSection(name="Project list and next-step summaries", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="New project creation", editable=True, edit_entry="New project", requires_confirmation=True
            ),
            SurfaceSection(name="Task add/manage", editable=True, edit_entry="Add task", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Project title/status",
                meaning="Project title and status",
                source="user_entered",
                stability="stable",
            ),
            SurfaceField(label="Next task", meaning="Next task label", source="user_entered", stability="stable"),
            SurfaceField(
                label="Activity timestamps",
                meaning="Project activity timestamps",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=1,
    ),
    # Tier 1: Habits
    "habits:dashboard": DomainSurfaceDefinition(
        domain="habits",
        surface_name="Habits Dashboard",
        purpose="Present recent adherence signals and today's plan without judgment.",
        primary_question="Did I keep my commitments recently?",
        primary_action="Review habits",
        read_only_sections=[
            SurfaceSection(name="Streak and status summaries", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="Log/confirm entry", editable=True, edit_entry="Log habit", requires_confirmation=False
            ),
            SurfaceSection(
                name="New habit creation", editable=True, edit_entry="New habit", requires_confirmation=True
            ),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="Habit name", meaning="Habit label", source="user_entered", stability="stable"),
            SurfaceField(
                label="Recent log status", meaning="Recent log status", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Streak count",
                meaning="Computed streak count",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=1,
    ),
    # Tier 2: Health
    "health:dashboard": DomainSurfaceDefinition(
        domain="health",
        surface_name="Health Dashboard",
        purpose="Show baseline health signals and trends without conclusions.",
        primary_question="How is my baseline and what needs attention?",
        primary_action="Review signals",
        read_only_sections=[
            SurfaceSection(name="Summary trends", editable=False),
        ],
        editable_sections=[
            SurfaceSection(name="Log update", editable=True, edit_entry="Log update", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="Metric labels", meaning="Metric labels", source="system_derived", stability="stable"),
            SurfaceField(
                label="User-entered values", meaning="Reported values", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Trend snapshots",
                meaning="Derived trend snapshots",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=2,
    ),
    # Tier 2: Relationships
    "relationships:dashboard": DomainSurfaceDefinition(
        domain="relationships",
        surface_name="Relationships Dashboard",
        purpose="Surface reconnection cues and recent interactions without scoring people.",
        primary_question="Who needs attention next?",
        primary_action="Review reconnection cues",
        read_only_sections=[
            SurfaceSection(name="Reconnection list", editable=False),
            SurfaceSection(name="Recent interactions", editable=False),
        ],
        editable_sections=[
            SurfaceSection(name="Add person", editable=True, edit_entry="Add person", requires_confirmation=True),
            SurfaceSection(
                name="Log interaction", editable=True, edit_entry="Log interaction", requires_confirmation=False
            ),
        ],
        confidence_rules=["suggested", "needs_review"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="Person name", meaning="Contact name", source="user_entered", stability="stable"),
            SurfaceField(
                label="Last interaction date",
                meaning="Most recent interaction date",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Reconnect cue",
                meaning="System-derived reconnection cue",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=2,
    ),
    # Tier 3: Skills
    "skills:dashboard": DomainSurfaceDefinition(
        domain="skills",
        surface_name="Skills Dashboard",
        purpose="Show current skill practice status and the next practice prompt.",
        primary_question="Am I improving and what should I practice next?",
        primary_action="Review practice plan",
        read_only_sections=[
            SurfaceSection(name="Skill summaries and recent sessions", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="New skill creation", editable=True, edit_entry="New skill", requires_confirmation=True
            ),
            SurfaceSection(name="Log practice", editable=True, edit_entry="Log practice", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="Skill name", meaning="Skill label", source="user_entered", stability="stable"),
            SurfaceField(
                label="Session count",
                meaning="Number of sessions",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Last practiced date",
                meaning="Most recent practice date",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=3,
    ),
    # Tier 4: Finance group
    "finance:journal": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Finance Journal",
        purpose="Provide a precise, read-first ledger of entries and review-required items.",
        primary_question="What changed and needs review?",
        primary_action="Review recent entries",
        read_only_sections=[
            SurfaceSection(name="Recent entries and summaries", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="New entry creation", editable=True, edit_entry="New entry", requires_confirmation=True
            ),
        ],
        confidence_rules=["informational", "needs_review"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Response ok", meaning="Response success flag", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response entries",
                meaning="Response journal entry list payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response total entries",
                meaning="Response total entry count",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response entry",
                meaning="Response journal entry payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response payload",
                meaning="Response payload container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response metadata",
                meaning="Response metadata container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(label="Entry id", meaning="Journal entry id", source="system_derived", stability="stable"),
            SurfaceField(
                label="Entry number", meaning="User-scoped entry number", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Entry description", meaning="Entry description", source="user_entered", stability="stable"
            ),
            SurfaceField(label="Occurred date", meaning="Entry date", source="system_derived", stability="stable"),
            SurfaceField(
                label="Line count", meaning="Number of journal lines", source="system_derived", stability="stable"
            ),
            SurfaceField(label="Debit total", meaning="Entry debit total", source="system_derived", stability="stable"),
            SurfaceField(
                label="Credit total", meaning="Entry credit total", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Journal lines", meaning="Journal line collection", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Journal line id", meaning="Journal line id", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Journal line account id",
                meaning="Account id for line",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Journal line account name",
                meaning="Account name for line",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Journal line debit", meaning="Line debit amount", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Journal line credit", meaning="Line credit amount", source="user_entered", stability="stable"
            ),
            SurfaceField(label="Journal line memo", meaning="Line memo", source="user_entered", stability="stable"),
            SurfaceField(label="Review status", meaning="Review status", source="system_derived", stability="stable"),
        ],
        tier=4,
    ),
    "finance:trial_balance": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Trial Balance",
        purpose="Present read-only balance positions as-of a date with optional rollups.",
        primary_question="What is the balance position as of now?",
        primary_action="Review balances",
        read_only_sections=[
            SurfaceSection(name="Account balances and rollups", editable=False),
        ],
        editable_sections=[
            SurfaceSection(name="Date filters", editable=True, edit_entry="Adjust date", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Response ok", meaning="Response success flag", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response accounts",
                meaning="Response account balance rows",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response categories",
                meaning="Response category balance rows",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response totals",
                meaning="Response period totals payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response months",
                meaning="Response monthly totals payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response payload",
                meaning="Response payload container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response metadata",
                meaning="Response metadata container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(label="Account id", meaning="Account id", source="system_derived", stability="stable"),
            SurfaceField(label="Account name", meaning="Account name", source="system_derived", stability="stable"),
            SurfaceField(label="Account code", meaning="Account code", source="system_derived", stability="stable"),
            SurfaceField(
                label="Account base type", meaning="Account base type", source="system_derived", stability="stable"
            ),
            SurfaceField(label="Category id", meaning="Category id", source="system_derived", stability="stable"),
            SurfaceField(label="Category name", meaning="Category name", source="system_derived", stability="stable"),
            SurfaceField(label="Normal balance", meaning="Normal balance", source="system_derived", stability="stable"),
            SurfaceField(label="Debit total", meaning="Debit balance", source="system_derived", stability="stable"),
            SurfaceField(label="Credit total", meaning="Credit balance", source="system_derived", stability="stable"),
            SurfaceField(label="Net balance", meaning="Net balance", source="system_derived", stability="stable"),
        ],
        tier=4,
    ),
    "finance:receivables": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Receivables",
        purpose="Track receivable principals and entries without mixing with payable flows.",
        primary_question="Which receivables need attention?",
        primary_action="Review trackers",
        read_only_sections=[
            SurfaceSection(name="Tracker list and totals", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="New tracker creation", editable=True, edit_entry="New tracker", requires_confirmation=True
            ),
            SurfaceSection(name="Add entry", editable=True, edit_entry="Add entry", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Response ok", meaning="Response success flag", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response items",
                meaning="Response receivable items payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response tracker",
                meaning="Response receivable tracker payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response page", meaning="Response page number", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response pages", meaning="Response total pages", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response total", meaning="Response total items", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response payload",
                meaning="Response payload container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response metadata",
                meaning="Response metadata container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(label="Receivable id", meaning="Receivable id", source="system_derived", stability="stable"),
            SurfaceField(
                label="Counterparty", meaning="Receivable counterparty", source="user_entered", stability="stable"
            ),
            SurfaceField(label="Principal", meaning="Receivable principal", source="user_entered", stability="stable"),
            SurfaceField(
                label="Start date", meaning="Receivable start date", source="user_entered", stability="stable"
            ),
            SurfaceField(label="Due date", meaning="Receivable due date", source="user_entered", stability="stable"),
            SurfaceField(
                label="Interest rate", meaning="Receivable interest rate", source="user_entered", stability="stable"
            ),
            SurfaceField(
                label="Receivable entry id", meaning="Receivable entry id", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Receivable tracker id",
                meaning="Receivable tracker id",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(label="Entry date", meaning="Entry date", source="user_entered", stability="stable"),
            SurfaceField(label="Entry amount", meaning="Entry amount", source="user_entered", stability="stable"),
            SurfaceField(label="Entry memo", meaning="Entry memo", source="user_entered", stability="stable"),
        ],
        tier=4,
    ),
    "finance:forecast": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Forecast",
        purpose="Show projected balances driven by scheduled events, with explicit manage mode.",
        primary_question="What is my projected cash position?",
        primary_action="Refresh forecast",
        read_only_sections=[
            SurfaceSection(name="Forecast table", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="Schedule creation", editable=True, edit_entry="New schedule", requires_confirmation=True
            ),
            SurfaceSection(name="Schedule edits", editable=True, edit_entry="Manage rows", requires_confirmation=True),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Response ok", meaning="Response success flag", source="system_derived", stability="stable"
            ),
            SurfaceField(
                label="Response forecast",
                meaning="Response forecast rows payload",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response payload",
                meaning="Response payload container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Response metadata",
                meaning="Response metadata container",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(label="Forecast date", meaning="Forecast date", source="system_derived", stability="stable"),
            SurfaceField(
                label="Projected balance",
                meaning="Projected balance",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=4,
    ),
    "finance:import": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Import 2.0",
        purpose="Provide a safe preview of import rows before committing.",
        primary_question="What will be imported if I proceed?",
        primary_action="Preview import",
        read_only_sections=[
            SurfaceSection(name="Preview table", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="Upload/select file", editable=True, edit_entry="Start import", requires_confirmation=True
            ),
            SurfaceSection(name="Commit import", editable=True, edit_entry="Commit import", requires_confirmation=True),
        ],
        confidence_rules=["needs_review"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="CSV row fields", meaning="Imported row fields", source="imported", stability="stable"),
            SurfaceField(
                label="Validation status",
                meaning="Validation status",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=4,
    ),
    "finance:accounts": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Accounts",
        purpose="Provide a read-only chart of accounts and category reference.",
        primary_question="What accounts exist and how are they grouped?",
        primary_action="Review accounts",
        read_only_sections=[
            SurfaceSection(name="Account list and balances", editable=False),
        ],
        editable_sections=[
            SurfaceSection(
                name="Category creation", editable=True, edit_entry="Create category", requires_confirmation=True
            ),
            SurfaceSection(name="Type filter", editable=True, edit_entry="Filter", requires_confirmation=False),
        ],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(label="Account name", meaning="Account name", source="system_derived", stability="stable"),
            SurfaceField(label="Account type", meaning="Account type", source="system_derived", stability="stable"),
            SurfaceField(label="Category", meaning="Account category", source="system_derived", stability="stable"),
            SurfaceField(label="Balance", meaning="Account balance", source="system_derived", stability="stable"),
        ],
        tier=4,
    ),
    "finance:transactions": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Transactions (redirect to Journal)",
        purpose="Provide a read-first pointer to the Finance Journal for transaction review.",
        primary_question="What changed recently?",
        primary_action="Review in Journal",
        read_only_sections=[
            SurfaceSection(name="Read-first guidance copy", editable=False),
        ],
        editable_sections=[],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Navigation target",
                meaning="Journal redirect target",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=4,
    ),
    "finance:dashboard": DomainSurfaceDefinition(
        domain="finance",
        surface_name="Finance Dashboard",
        purpose="Provide a read-first snapshot of balances, recent activity, and near-term forecast.",
        primary_question="Where do I stand right now, and what changed recently?",
        primary_action="Review transactions",
        read_only_sections=[
            SurfaceSection(name="Summary tiles", editable=False),
            SurfaceSection(name="Recent transactions", editable=False),
            SurfaceSection(name="Schedule", editable=False),
            SurfaceSection(name="Forecast", editable=False),
        ],
        editable_sections=[],
        confidence_rules=["informational"],
        insight_contracts=[],
        data_fields=[
            SurfaceField(
                label="Account counts and balances",
                meaning="Account counts and balances",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Recent transactions",
                meaning="Recent transaction summaries",
                source="system_derived",
                stability="stable",
            ),
            SurfaceField(
                label="Forecast snapshots",
                meaning="Forecast snapshots",
                source="system_derived",
                stability="stable",
            ),
        ],
        tier=4,
    ),
}


def list_domain_surfaces(tier: Optional[int] = None) -> Iterable[DomainSurfaceDefinition]:
    """List domain surface definitions, optionally filtered by tier."""
    values = DOMAIN_SURFACE_CONTRACTS.values()
    if tier is None:
        return values
    return [surface for surface in values if surface.tier == tier]


__all__ = [
    "DomainSurfaceDefinition",
    "SurfaceField",
    "SurfaceSection",
    "DOMAIN_SURFACE_CONTRACTS",
    "list_domain_surfaces",
]
