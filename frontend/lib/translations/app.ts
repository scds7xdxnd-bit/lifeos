import type { Lang } from '@/components/landing/translations'

/* ── Login page ─────────────────────────────────────────────────────────── */

export interface LoginTranslations {
  backToHome: string
  welcomeBack: string
  joinAlpha: string
  acceptInvite: string
  signInSub: string
  registerSub: string
  acceptInviteSub: string
  limitedSpots: string
  email: string
  invitedEmail: string
  password: string
  confirmPassword: string
  inviteToken: string
  emailPlaceholder: string
  passwordPlaceholder: string
  confirmPasswordPlaceholder: string
  invitePlaceholder: string
  pleaseWait: string
  continue: string
  createAccount: string
  finishSetup: string
  finishSetupSignIn: string
  passwordMismatch: string
  noAccount: string
  register: string
  haveAccount: string
  signIn: string
}

/* ── Onboarding ─────────────────────────────────────────────────────────── */

export interface OnboardingTranslations {
  step1of2: string
  step2of2: string
  whatToTrack: string
  whatToTrackSub: string
  connectCalendar: string
  connectCalendarSub: string
  selected: string
  back: string
  continue: string
  saving: string
  errorDomain: string
  errorCalendar: string
  errorGeneric: string
  domains: { id: string; label: string; description: string }[]
  calendar: { id: string; label: string; subtitle: string }[]
  processing: {
    title: string
    subtitle: string
    complete: string
    items: { label: string; status: string }[]
    connected: string
    digitalRhythm: string
    digitalRhythmDesc: string
    processing: string
    intentMapping: string
    intentMappingDesc: string
  }
}

/* ── App shell ──────────────────────────────────────────────────────────── */

export interface HeaderTranslations {
  calendar: string
  inquiry: string
  finances: string
  health: string
  habits: string
  skills: string
  signOut: string
}

export interface FooterTranslations {
  tagline: string
  philosophy: string
}

export interface LayoutTranslations {
  loading: string
}

/* ── Domain pages ───────────────────────────────────────────────────────── */

export interface CalendarPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  today: string
  year: string
  month: string
  week: string
  day: string
  weekdaySun: string
  weekdayMon: string
  weekdayTue: string
  weekdayWed: string
  weekdayThu: string
  weekdayFri: string
  weekdaySat: string
  addEvent: string
  cancel: string
  newEvent: string
  titleLabel: string
  titlePlaceholder: string
  location: string
  optional: string
  start: string
  end: string
  allDay: string
  saving: string
  saveEvent: string
  events: string
  noEvents: string
}

export interface FinancesPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  comingSoonTitle: string
  comingSoonBody: string
}

export interface HealthPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  comingSoonTitle: string
  comingSoonBody: string
}

export interface HabitsPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  newHabit: string
  cancel: string
  name: string
  namePlaceholder: string
  schedule: string
  daily: string
  weekly: string
  custom: string
  description: string
  optional: string
  creating: string
  createHabit: string
  yourHabits: string
  noHabits: string
  log: string
  logged: string
  done: string
  today: string
  yesterday: string
  daysAgo: string
  dayStreak: string
  undo: string
  thisMonth: string
  emptyTitle: string
  emptyBody: string
  emptyAction: string
  deleteTitle: string
  deleteBody: string
  deleteConfirm: string
  deleteCancel: string
  detailTitle: string
  currentStreak: string
  longestStreak: string
  completionRate: string
  totalLogs: string
  last30Days: string
  yearlyHeatmap: string
  selectHabit: string
  days: string
  noData: string
  dueIn: string
  dueSoon: string
  overdue: string
}

export interface SkillsPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  newSkill: string
  cancel: string
  name: string
  namePlaceholder: string
  category: string
  categoryPlaceholder: string
  description: string
  optional: string
  creating: string
  createSkill: string
  logPractice: string
  durationLabel: string
  notes: string
  logging: string
  logSession: string
  yourSkills: string
  noSkills: string
  practice: string
  sessions: string
  sessionsLabel: string
  hoursLabel: string
  milestonesLabel: string
  minuteShort: string
  hourShort: string
  weekShort: string
  streak: string
  summaryTotalHours: string
  summarySessions: string
  summaryAtRisk: string
  summaryActive: string
  migrationNoticeTitle: string
  migrationNoticeBody: string
  stepOf2: string
  skillBasics: string
  goalEndpoint: string
  rolloutGateTitle: string
  rolloutGateBody: string
  continueAction: string
  back: string
  goalType: string
  targetValue: string
  quickPresets: string
  skillPreview: string
  preview: string
  goalTypeLabel: string
  creationSnapshot: string
  creationSnapshotBody: string
  studioHeading: string
  signalClearSkillName: string
  signalCategoryContextAdded: string
  signalGoalEndpointSelected: string
  signalDescriptionIncludesIntent: string
  tipNameSkillFirst: string
  tipGoalOptional: string
  tipStrongEndpointSet: string
  goalTypeHelpSessions: string
  goalTypeHelpHours: string
  goalTypeHelpMilestones: string
  unit: string
  goalSnapshot: string
  doneSoFar: string
  targetingTotal: string
  pace: string
  eta: string
  notEnoughDataYet: string
  notAvailableYet: string
  milestoneQualitativeHint: string
  quickActions: string
  raiseTargetBy10: string
  extendTimelineBy14d: string
  deadlineOptional: string
  saveGoal: string
  saving: string
  continuePracticeTitle: string
  suggested: string
  practiceStep: string
  auto: string
  recommendedPrefix: string
  recommendedFallback: string
  pacingCue: string
  pacingCueBody: string
  sessionSaved: string
  totalNowAround: string
  nextUpPrefix: string
  nextRecommendedAction: string
  setGoal: string
  editGoal: string
  continuePractice: string
  viewInsights: string
  insightsTitle: string
  reviewGoalProgress: string
  goalProgress: string
  nowLabel: string
  nextLabel: string
  riskLabel: string
  nowTowardGoal: string
  nowPracticeVolume: string
  riskNone: string
  riskNeedMoreHistory: string
  density: string
  densityCompact: string
  densityComfortable: string
  sortBy: string
  sortUrgency: string
  sortMomentum: string
  sortAlphabetical: string
  needsAttention: string
  attentionStalled: string
  attentionBelowPace: string
  attentionDeadlineRisk: string
  last7Days: string
  weeklyCadence: string
  weeklyCadenceAria: string
  nextActionSetupGoalThenPractice: string
  nextActionKeepEndpointStable: string
  nextActionRecoverMomentum: string
  nextActionSustainRhythm: string
  nextActionFocusedSession: string
  forecast: string
  projectedSummary: string
  forecastScenarios: string
  scenarioKeepPace: string
  scenarioPlusOneSession: string
  scenarioPlusThirtyMinutes: string
  scenarioProjectedProgress: string
  statusCompleted: string
  statusAtRisk: string
  statusOnTrack: string
  statusAhead: string
  errorGoalRequired: string
  errorCreateFailed: string
  errorUpdateGoalFailed: string
  errorTargetValueRequired: string
  statusInsufficientData: string
  forecastReasonCompleted: string
  forecastReasonNoGoalConfigured: string
  forecastReasonNoRecentSessions: string
  forecastReasonNeedsConsistency: string
  forecastReasonQualitativeGoal: string
  forecastReasonNeedMoreHistory: string
  forecastReasonOnTrack: string
  celebrationSummary: string
  deleteTitle: string
  deleteBody: string
  deleteConfirm: string
  deleteCancel: string
}

export interface ProjectsPageTranslations {
  title: string
  subtitle: string
  newProject: string
  cancel: string
  createProject: string
  name: string
  namePlaceholder: string
  targetDate: string
  description: string
  optional: string
  creating: string
  projects: string
  loading: string
  noProjects: string
  done: string
  delete: string
  tasks: string
  addTask: string
  taskTitleLabel: string
  taskTitlePlaceholder: string
  taskNotes: string
  adding: string
  add: string
  noTasks: string
  complete: string
}

/* ── Aggregate ──────────────────────────────────────────────────────────── */

export interface AppTranslations {
  login: LoginTranslations
  onboarding: OnboardingTranslations
  header: HeaderTranslations
  footer: FooterTranslations
  layout: LayoutTranslations
  calendar: CalendarPageTranslations
  finances: FinancesPageTranslations
  health: HealthPageTranslations
  habits: HabitsPageTranslations
  skills: SkillsPageTranslations
  projects: ProjectsPageTranslations
}

/* ═══════════════════════════════════════════════════════════════════════════
   English
   ═══════════════════════════════════════════════════════════════════════════ */

const en: AppTranslations = {
  login: {
    backToHome: 'Back to home',
    welcomeBack: 'Welcome back',
    joinAlpha: 'Join the alpha',
    acceptInvite: 'Accept your invite',
    signInSub: 'Sign in to your archive.',
    registerSub: 'Private alpha \u2014 invite token required.',
    acceptInviteSub: 'Set your password to activate your account and continue to onboarding.',
    limitedSpots: 'Limited spots',
    email: 'Email',
    invitedEmail: 'Invited email',
    password: 'Password',
    confirmPassword: 'Confirm password',
    inviteToken: 'Invite token',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: 'Enter password',
    confirmPasswordPlaceholder: 'Confirm password',
    invitePlaceholder: 'Paste your invite token',
    pleaseWait: 'Please wait\u2026',
    continue: 'Continue',
    createAccount: 'Create Account',
    finishSetup: 'Set Password & Continue',
    finishSetupSignIn: 'Password set. Please sign in to continue.',
    passwordMismatch: 'Passwords do not match.',
    noAccount: 'No account?',
    register: 'Register',
    haveAccount: 'Have an account?',
    signIn: 'Sign in',
  },
  onboarding: {
    step1of2: 'Step 1 of 2',
    step2of2: 'Step 2 of 2',
    whatToTrack: 'What would you like to track?',
    whatToTrackSub: 'Choose the areas of your life you\u2019d like to organize.',
    connectCalendar: 'Connect your calendar',
    connectCalendarSub: 'Import your schedule to let LifeOS understand your time.',
    selected: 'selected',
    back: 'Back',
    continue: 'Continue',
    saving: 'Saving\u2026',
    errorDomain: 'Please select at least one domain to continue.',
    errorCalendar: 'Please select a calendar option to continue.',
    errorGeneric: 'Something went wrong. Please try again.',
    domains: [
      { id: 'finance', label: 'Finances', description: 'Track spending, budgets & goals' },
      { id: 'health', label: 'Health', description: 'Biometrics, workouts & nutrition' },
      { id: 'habits', label: 'Habits', description: 'Build routines & track streaks' },
      { id: 'skills', label: 'Skills', description: 'Practice sessions & growth' },
    ],
    calendar: [
      { id: 'google', label: 'Google Calendar', subtitle: 'Sync events from Google Workspace' },
      { id: 'apple', label: 'Apple Calendar', subtitle: 'Sync events from iCloud' },
      { id: 'skip', label: 'Skip for now', subtitle: 'You can connect a calendar later' },
    ],
    processing: {
      title: 'Listening to the Archive...',
      subtitle: 'Your personal digital ecosystem is being harmonized.',
      complete: 'Complete',
      items: [
        { label: 'Habit Patterns', status: 'FOUND' },
        { label: 'Weekly Rhythm', status: 'ANALYZING' },
        { label: 'Focus Windows', status: 'MAPPING' },
        { label: 'Growth Trajectory', status: 'CONNECTED' },
      ],
      connected: 'CONNECTED',
      digitalRhythm: 'Digital Rhythm',
      digitalRhythmDesc: 'Aligning with your focus cycles and natural downtime.',
      processing: 'PROCESSING',
      intentMapping: 'Intent Mapping',
      intentMappingDesc: 'Translating logs into actionable wisdom for your next chapter.',
    },
  },
  header: {
    calendar: 'Calendar',
    inquiry: 'Inquiry',
    finances: 'Finances',
    health: 'Health',
    habits: 'Habits',
    skills: 'Skills',
    signOut: 'Sign out',
  },
  footer: {
    tagline: 'Your life, clearly.',
    philosophy: 'Deterministic intelligence \u00b7 No ML autonomy',
  },
  layout: {
    loading: 'Opening your sanctuary\u2026',
  },
  calendar: {
    eyebrow: 'Timeline',
    title: 'Calendar',
    subtitle: 'Manage calendar events for inquiry analysis.',
    today: 'Today',
    year: 'Year',
    month: 'Month',
    week: 'Week',
    day: 'Day',
    weekdaySun: 'Sun',
    weekdayMon: 'Mon',
    weekdayTue: 'Tue',
    weekdayWed: 'Wed',
    weekdayThu: 'Thu',
    weekdayFri: 'Fri',
    weekdaySat: 'Sat',
    addEvent: 'Add Event',
    cancel: 'Cancel',
    newEvent: 'New Event',
    titleLabel: 'Title',
    titlePlaceholder: 'Event title',
    location: 'Location',
    optional: 'Optional',
    start: 'Start',
    end: 'End',
    allDay: 'All day',
    saving: 'Saving\u2026',
    saveEvent: 'Save Event',
    events: 'Events',
    noEvents: 'No events yet. Add your first event above.',
  },
  finances: {
    eyebrow: 'Domain',
    title: 'Finances',
    subtitle: 'Track spending, budgets, and goals. Your financial story, told clearly.',
    comingSoonTitle: 'Finance domain coming soon',
    comingSoonBody: 'Accounts, journal entries, transactions, and forecasts will appear here once the frontend integration is complete.',
  },
  health: {
    eyebrow: 'Domain',
    title: 'Health',
    subtitle: 'Biometrics, workouts, and nutrition. A gentle record of how you feel.',
    comingSoonTitle: 'Health domain coming soon',
    comingSoonBody: 'Biometrics, workout logs, and nutrition tracking will appear here once the frontend integration is complete.',
  },
  habits: {
    eyebrow: 'Discipline',
    title: 'Habits',
    subtitle: 'Track daily habits to build inquiry data.',
    newHabit: 'New Habit',
    cancel: 'Cancel',
    name: 'Name',
    namePlaceholder: 'e.g. Morning run',
    schedule: 'Schedule',
    daily: 'Daily',
    weekly: 'Weekly',
    custom: 'Custom',
    description: 'Description',
    optional: 'Optional',
    creating: 'Creating\u2026',
    createHabit: 'Create Habit',
    yourHabits: 'Your Habits',
    noHabits: 'No habits yet. Create your first habit above.',
    log: 'Log',
    logged: 'logged',
    done: 'Done',
    today: 'Today',
    yesterday: 'Yesterday',
    daysAgo: 'days ago',
    dayStreak: 'day streak',
    undo: 'Undo',
    thisMonth: 'this month',
    emptyTitle: 'Start building your rhythm',
    emptyBody: 'Small, consistent actions compound into meaningful change. Create your first habit and let the streaks tell the story.',
    emptyAction: 'Create Your First Habit',
    deleteTitle: 'Delete habit?',
    deleteBody: 'This will permanently delete {name} and all its logs. This cannot be undone.',
    deleteConfirm: 'Delete',
    deleteCancel: 'Cancel',
    detailTitle: 'Habit Detail',
    currentStreak: 'Current Streak',
    longestStreak: 'Longest Streak',
    completionRate: 'Completion Rate',
    totalLogs: 'Total Logs',
    last30Days: 'Last 30 Days',
    yearlyHeatmap: 'Yearly Heatmap',
    selectHabit: 'Select a habit to see its analytics',
    days: 'days',
    noData: 'No data yet',
    dueIn: 'Due in {time}',
    dueSoon: 'Due soon',
    overdue: 'Overdue by {time}',
  },
  skills: {
    eyebrow: 'Mastery',
    title: 'Skills',
    subtitle: 'Track skills and practice sessions for inquiry analysis.',
    newSkill: 'New Skill',
    cancel: 'Cancel',
    name: 'Name',
    namePlaceholder: 'e.g. Piano',
    category: 'Category',
    categoryPlaceholder: 'e.g. Music',
    description: 'Description',
    optional: 'Optional',
    creating: 'Creating\u2026',
    createSkill: 'Create Skill',
    logPractice: 'Log Practice',
    durationLabel: 'Duration (minutes)',
    notes: 'Notes',
    logging: 'Logging\u2026',
    logSession: 'Log Session',
    yourSkills: 'Your Skills',
    noSkills: 'No skills yet. Create your first skill above.',
    practice: 'Practice',
    sessions: 'sessions',
    sessionsLabel: 'Sessions',
    hoursLabel: 'Hours',
    milestonesLabel: 'Milestones',
    minuteShort: 'm',
    hourShort: 'h',
    weekShort: 'week',
    streak: 'd streak',
    summaryTotalHours: 'Total Hours',
    summarySessions: 'Sessions',
    summaryAtRisk: 'At Risk',
    summaryActive: 'Active',
    migrationNoticeTitle: 'Migration Notice',
    migrationNoticeBody: 'Existing skills were preserved with safe defaults. You can refine any goal endpoint from each skill path.',
    stepOf2: 'Step {step} of 2',
    skillBasics: 'Skill Basics',
    goalEndpoint: 'Goal Endpoint',
    rolloutGateTitle: 'Rollout Gate',
    rolloutGateBody: 'Goals are required for new skills in this rollout. Pick a goal type and target value before creating.',
    continueAction: 'Continue',
    back: 'Back',
    goalType: 'Goal Type',
    targetValue: 'Target Value',
    quickPresets: 'Quick Presets',
    skillPreview: 'Live Reflection',
    preview: 'Preview',
    goalTypeLabel: 'Goal type',
    creationSnapshot: 'Creation Snapshot',
    creationSnapshotBody: 'This skill will start with a clean baseline and become forecast-ready once a goal endpoint is set.',
    studioHeading: 'You are shaping a practice rhythm that can actually stick.',
    signalClearSkillName: 'Clear skill name',
    signalCategoryContextAdded: 'Category context added',
    signalGoalEndpointSelected: 'Goal endpoint selected',
    signalDescriptionIncludesIntent: 'Description includes intent',
    tipNameSkillFirst: 'Name the skill first so your plan feels concrete and easy to return to.',
    tipGoalOptional: 'You can leave the goal blank for now and set it later from {editGoal}.',
    tipStrongEndpointSet: 'Strong endpoint set. This gives path guidance and forecast a clearer baseline.',
    goalTypeHelpSessions: 'Use sessions for consistency goals. The target value is how many practice sessions you want to log.',
    goalTypeHelpHours: 'Use hours for volume goals. The target value is total hours you want to accumulate.',
    goalTypeHelpMilestones: 'Use milestones for qualitative checkpoints. The target value is how many milestones you want to complete.',
    unit: 'Unit',
    goalSnapshot: 'Goal Snapshot',
    doneSoFar: 'done so far',
    targetingTotal: 'targeting {target} total.',
    pace: 'Pace',
    eta: 'ETA',
    notEnoughDataYet: 'not enough data yet',
    notAvailableYet: 'not available yet',
    milestoneQualitativeHint: 'Milestone goals are qualitative. Use this target as directional progress and update milestones as you complete key checkpoints.',
    quickActions: 'Quick Actions',
    raiseTargetBy10: 'Raise target +10%',
    extendTimelineBy14d: 'Extend timeline +14d',
    deadlineOptional: 'Deadline (Optional)',
    saveGoal: 'Save Goal',
    saving: 'Saving...',
    continuePracticeTitle: 'Continue Practice - {skill}',
    suggested: 'Suggested',
    practiceStep: 'Practice Step',
    auto: 'Auto',
    recommendedPrefix: 'Recommended: {step}',
    recommendedFallback: 'A recommended step will appear when enough path context is available.',
    pacingCue: 'Pacing Cue',
    pacingCueBody: 'Suggested duration is based on your recent rhythm: around {minutes} minutes.',
    sessionSaved: 'Session Saved',
    totalNowAround: 'Total now around {total}.',
    nextUpPrefix: 'Next up: {step}',
    nextRecommendedAction: 'Next Recommended Action',
    setGoal: 'Set Goal',
    editGoal: 'Edit Goal',
    continuePractice: 'Continue Practice',
    viewInsights: 'View Insights',
    insightsTitle: 'Insights - {skill}',
    reviewGoalProgress: 'Review Goal Progress',
    goalProgress: 'Goal Progress',
    nowLabel: 'Now',
    nextLabel: 'Next',
    riskLabel: 'Risk',
    nowTowardGoal: '{progress} of goal reached.',
    nowPracticeVolume: '{minutes} practiced across {sessions} sessions.',
    riskNone: 'No immediate risk signal.',
    riskNeedMoreHistory: 'Need a bit more history for stable risk guidance.',
    density: 'Density',
    densityCompact: 'Compact',
    densityComfortable: 'Comfortable',
    sortBy: 'Sort',
    sortUrgency: 'Urgency',
    sortMomentum: 'Momentum',
    sortAlphabetical: 'A-Z',
    needsAttention: 'Needs Attention',
    attentionStalled: 'stalled',
    attentionBelowPace: 'below pace',
    attentionDeadlineRisk: 'deadline risk',
    last7Days: '{count} in last 7d',
    weeklyCadence: 'Weekly Cadence',
    weeklyCadenceAria: 'Weekly cadence for {name}',
    nextActionSetupGoalThenPractice: 'Next action: set a goal endpoint, then continue practice.',
    nextActionKeepEndpointStable: 'Next action: continue practice to keep this endpoint stable.',
    nextActionRecoverMomentum: 'Next action: log a short session today to recover momentum.',
    nextActionSustainRhythm: 'Next action: continue practice to sustain this weekly rhythm.',
    nextActionFocusedSession: 'Next action: one focused session today keeps this skill moving.',
    forecast: 'Forecast ({days}d)',
    projectedSummary: 'Projected {minutes} and {sessions} sessions.',
    forecastScenarios: 'Forecast Scenarios',
    scenarioKeepPace: 'Keep Pace',
    scenarioPlusOneSession: '+1 Session',
    scenarioPlusThirtyMinutes: '+30 Minutes',
    scenarioProjectedProgress: 'Scenario progress: {progress} of goal.',
    statusCompleted: 'Completed',
    statusAtRisk: 'At Risk',
    statusOnTrack: 'On Track',
    statusAhead: 'Ahead',
    errorGoalRequired: 'Goal endpoint is required in this rollout. Set a goal to continue.',
    errorCreateFailed: 'Unable to create skill. Please review inputs and try again.',
    errorUpdateGoalFailed: 'Unable to update goal. Please try again.',
    errorTargetValueRequired: 'Target value must be greater than zero.',
    statusInsufficientData: 'Insufficient Data',
    forecastReasonCompleted: 'Your current trajectory already satisfies this goal window.',
    forecastReasonNoGoalConfigured: 'No goal is configured yet, so guidance is limited until one is set.',
    forecastReasonNoRecentSessions: 'Recent activity is low, so your goal trajectory may slip this week.',
    forecastReasonNeedsConsistency: 'Recent patterns suggest this goal needs extra consistency.',
    forecastReasonQualitativeGoal: 'This goal type is qualitative, so we show activity guidance without numeric projection.',
    forecastReasonNeedMoreHistory: 'A little more activity history is needed for stable guidance.',
    forecastReasonOnTrack: 'Recent consistency suggests your current pace is sustainable.',
    celebrationSummary: '+{minutes} min, +{sessions} session, streak delta +{streak}.',
    deleteTitle: 'Delete skill?',
    deleteBody: 'This will permanently delete {name} and all practice history. This cannot be undone.',
    deleteConfirm: 'Delete',
    deleteCancel: 'Cancel',
  },
  projects: {
    title: 'Projects',
    subtitle: 'Manage projects and tasks for inquiry analysis.',
    newProject: 'New Project',
    cancel: 'Cancel',
    createProject: 'Create Project',
    name: 'Name',
    namePlaceholder: 'e.g. Launch website',
    targetDate: 'Target date',
    description: 'Description',
    optional: 'Optional',
    creating: 'Creating\u2026',
    projects: 'Projects',
    loading: 'Loading\u2026',
    noProjects: 'No projects yet. Create one above.',
    done: 'Done',
    delete: 'Delete',
    tasks: 'Tasks',
    addTask: 'Add Task',
    taskTitleLabel: 'Title',
    taskTitlePlaceholder: 'Task title',
    taskNotes: 'Notes',
    adding: 'Adding\u2026',
    add: 'Add',
    noTasks: 'No tasks yet.',
    complete: 'Complete',
  },
}

/* ═══════════════════════════════════════════════════════════════════════════
   Korean
   ═══════════════════════════════════════════════════════════════════════════ */

const ko: AppTranslations = {
  login: {
    backToHome: '\ud648\uc73c\ub85c \ub3cc\uc544\uac00\uae30',
    welcomeBack: '\ub2e4\uc2dc \uc624\uc168\uad70\uc694',
    joinAlpha: '\uc54c\ud30c\uc5d0 \ud569\ub958\ud558\uae30',
    acceptInvite: '\ucd08\ub300 \uc218\ub77d\ud558\uae30',
    signInSub: '\uc544\uce74\uc774\ube0c\uc5d0 \ub85c\uadf8\uc778\ud558\uc138\uc694.',
    registerSub: '\ud504\ub77c\uc774\ube57 \uc54c\ud30c \u2014 \ucd08\ub300 \ud1a0\ud070\uc774 \ud544\uc694\ud569\ub2c8\ub2e4.',
    acceptInviteSub: '\ube44\ubc00\ubc88\ud638\ub97c \uc124\uc815\ud558\uba74 \uacc4\uc815\uc774 \ud65c\uc131\ud654\ub418\uace0 \uc628\ubcf4\ub529\uc73c\ub85c \uc9c4\ud589\ub429\ub2c8\ub2e4.',
    limitedSpots: '\uc778\uc6d0 \uc81c\ud55c',
    email: '\uc774\uba54\uc77c',
    invitedEmail: '\ucd08\ub300\ub41c \uc774\uba54\uc77c',
    password: '\ube44\ubc00\ubc88\ud638',
    confirmPassword: '\ube44\ubc00\ubc88\ud638 \ud655\uc778',
    inviteToken: '\ucd08\ub300 \ud1a0\ud070',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: '\ube44\ubc00\ubc88\ud638 \uc785\ub825',
    confirmPasswordPlaceholder: '\ube44\ubc00\ubc88\ud638 \ub2e4\uc2dc \uc785\ub825',
    invitePlaceholder: '\ucd08\ub300 \ud1a0\ud070 \ubd99\uc5ec\ub123\uae30',
    pleaseWait: '\uc7a0\uc2dc\ub9cc\uc694\u2026',
    continue: '\uacc4\uc18d',
    createAccount: '\uacc4\uc815 \ub9cc\ub4e4\uae30',
    finishSetup: '\ube44\ubc00\ubc88\ud638 \uc124\uc815\ud558\uace0 \uacc4\uc18d',
    finishSetupSignIn: '\ube44\ubc00\ubc88\ud638\uac00 \uc124\uc815\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \uacc4\uc18d\ud558\ub824\uba74 \ub85c\uadf8\uc778\ud558\uc138\uc694.',
    passwordMismatch: '\ube44\ubc00\ubc88\ud638\uac00 \uc77c\uce58\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.',
    noAccount: '\uacc4\uc815\uc774 \uc5c6\uc73c\uc2e0\uac00\uc694?',
    register: '\uac00\uc785\ud558\uae30',
    haveAccount: '\uc774\ubbf8 \uacc4\uc815\uc774 \uc788\uc73c\uc2e0\uac00\uc694?',
    signIn: '\ub85c\uadf8\uc778',
  },
  onboarding: {
    step1of2: '1\ub2e8\uacc4 / 2',
    step2of2: '2\ub2e8\uacc4 / 2',
    whatToTrack: '\ubb34\uc5c7\uc744 \ucd94\uc801\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?',
    whatToTrackSub: '\uc815\ub9ac\ud558\uace0 \uc2f6\uc740 \uc0b6\uc758 \uc601\uc5ed\uc744 \uc120\ud0dd\ud558\uc138\uc694.',
    connectCalendar: '\uce98\ub9b0\ub354 \uc5f0\uacb0',
    connectCalendarSub: 'LifeOS\uac00 \uc2dc\uac04\uc744 \uc774\ud574\ud560 \uc218 \uc788\ub3c4\ub85d \uc77c\uc815\uc744 \uac00\uc838\uc624\uc138\uc694.',
    selected: '\uc120\ud0dd\ub428',
    back: '\uc774\uc804',
    continue: '\uacc4\uc18d',
    saving: '\uc800\uc7a5 \uc911\u2026',
    errorDomain: '\uacc4\uc18d\ud558\ub824\uba74 \ucd5c\uc18c \ud558\ub098\uc758 \ub3c4\uba54\uc778\uc744 \uc120\ud0dd\ud558\uc138\uc694.',
    errorCalendar: '\uacc4\uc18d\ud558\ub824\uba74 \uce98\ub9b0\ub354 \uc635\uc158\uc744 \uc120\ud0dd\ud558\uc138\uc694.',
    errorGeneric: '\ubb38\uc81c\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \uc8fc\uc138\uc694.',
    domains: [
      { id: 'finance', label: '\uc7ac\uc815', description: '\uc9c0\ucd9c, \uc608\uc0b0, \ubaa9\ud45c\ub97c \ucd94\uc801\ud558\uc138\uc694' },
      { id: 'health', label: '\uac74\uac15', description: '\uc0dd\uccb4\uc9c0\ud45c, \uc6b4\ub3d9, \uc601\uc591 \uad00\ub9ac' },
      { id: 'habits', label: '\uc2b5\uad00', description: '\ub8e8\ud2f4\uc744 \ub9cc\ub4e4\uace0 \uc5f0\uc18d \uae30\ub85d\uc744 \ucd94\uc801\ud558\uc138\uc694' },
      { id: 'skills', label: '\uc2a4\ud0ac', description: '\uc5f0\uc2b5 \uc138\uc158\uacfc \uc131\uc7a5 \uae30\ub85d' },
    ],
    calendar: [
      { id: 'google', label: 'Google \uce98\ub9b0\ub354', subtitle: 'Google Workspace \uc77c\uc815 \ub3d9\uae30\ud654' },
      { id: 'apple', label: 'Apple \uce98\ub9b0\ub354', subtitle: 'iCloud \uc77c\uc815 \ub3d9\uae30\ud654' },
      { id: 'skip', label: '\ub098\uc911\uc5d0 \ud558\uae30', subtitle: '\ub098\uc911\uc5d0 \uce98\ub9b0\ub354\ub97c \uc5f0\uacb0\ud560 \uc218 \uc788\uc5b4\uc694' },
    ],
    processing: {
      title: '\uc544\uce74\uc774\ube0c\ub97c \uc77d\ub294 \uc911...',
      subtitle: '\ub370\uc774\ud130 \uc2a4\ud2b8\ub9bc \uc5f0\uacb0 \uc911...',
      complete: '\uc644\ub8cc',
      items: [
        { label: '\uc2b5\uad00 \ud328\ud134', status: '\ubc1c\uacac\ub428' },
        { label: '\uc8fc\uac04 \ub9ac\ub4ec', status: '\ubd84\uc11d \uc911' },
        { label: '\uc9d1\uc911 \uc2dc\uac04\ub300', status: '\ub9e4\ud551 \uc911' },
        { label: '\uc131\uc7a5 \uada4\uc801', status: '\uc5f0\uacb0\ub428' },
      ],
      connected: '\uc5f0\uacb0\ub428',
      digitalRhythm: '\ub514\uc9c0\ud138 \ub9ac\ub4ec',
      digitalRhythmDesc: '\uc9d1\uc911 \uc8fc\uae30\uc640 \uc790\uc5f0\uc2a4\ub7ec\uc6b4 \ud734\uc2dd \uc2dc\uac04\uc5d0 \ub9de\ucda4.',
      processing: '\ucc98\ub9ac \uc911',
      intentMapping: '\uc758\ub3c4 \ub9e4\ud551',
      intentMappingDesc: '\ub85c\uadf8\ub97c \ub2e4\uc74c \uc7a5\uc744 \uc704\ud55c \uc2e4\ud589 \uac00\ub2a5\ud55c \uc9c0\ud61c\ub85c \ubcc0\ud658.',
    },
  },
  header: {
    calendar: '\uce98\ub9b0\ub354',
    inquiry: '\uc9c8\uc758',
    finances: '\uc7ac\uc815',
    health: '\uac74\uac15',
    habits: '\uc2b5\uad00',
    skills: '\uc2a4\ud0ac',
    signOut: '\ub85c\uadf8\uc544\uc6c3',
  },
  footer: {
    tagline: '\ub0b4 \uc0b6, \uba85\ud655\ud558\uac8c.',
    philosophy: '\uacb0\uc815\ub860\uc801 \uc778\ud154\ub9ac\uc804\uc2a4 \u00b7 ML \uc790\uc728\uc131 \ubc30\uc81c',
  },
  layout: {
    loading: '\uc131\uc5ed\uc744 \uc5ec\ub294 \uc911\u2026',
  },
  calendar: {
    eyebrow: '\ud0c0\uc784\ub77c\uc778',
    title: '\uce98\ub9b0\ub354',
    subtitle: '\uc9c8\uc758 \ubd84\uc11d\uc744 \uc704\ud55c \uce98\ub9b0\ub354 \uc774\ubca4\ud2b8\ub97c \uad00\ub9ac\ud558\uc138\uc694.',
    today: '\uc624\ub298',
    year: '\ub144',
    month: '\uc6d4',
    week: '\uc8fc',
    day: '\uc77c',
    weekdaySun: '\uc77c',
    weekdayMon: '\uc6d4',
    weekdayTue: '\ud654',
    weekdayWed: '\uc218',
    weekdayThu: '\ubaa9',
    weekdayFri: '\uae08',
    weekdaySat: '\ud1a0',
    addEvent: '\uc774\ubca4\ud2b8 \ucd94\uac00',
    cancel: '\ucde8\uc18c',
    newEvent: '\uc0c8 \uc774\ubca4\ud2b8',
    titleLabel: '\uc81c\ubaa9',
    titlePlaceholder: '\uc774\ubca4\ud2b8 \uc81c\ubaa9',
    location: '\uc7a5\uc18c',
    optional: '\uc120\ud0dd\uc0ac\ud56d',
    start: '\uc2dc\uc791',
    end: '\uc885\ub8cc',
    allDay: '\uc885\uc77c',
    saving: '\uc800\uc7a5 \uc911\u2026',
    saveEvent: '\uc774\ubca4\ud2b8 \uc800\uc7a5',
    events: '\uc774\ubca4\ud2b8',
    noEvents: '\uc544\uc9c1 \uc774\ubca4\ud2b8\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc704\uc5d0\uc11c \uccab \uc774\ubca4\ud2b8\ub97c \ucd94\uac00\ud558\uc138\uc694.',
  },
  finances: {
    eyebrow: '\ub3c4\uba54\uc778',
    title: '\uc7ac\uc815',
    subtitle: '\uc9c0\ucd9c, \uc608\uc0b0, \ubaa9\ud45c\ub97c \ucd94\uc801\ud558\uc138\uc694. \ub098\uc758 \uc7ac\uc815 \uc774\uc57c\uae30\ub97c \uba85\ud655\ud558\uac8c.',
    comingSoonTitle: '\uc7ac\uc815 \ub3c4\uba54\uc778 \uace7 \ucd9c\uc2dc',
    comingSoonBody: '\ud504\ub860\ud2b8\uc5d4\ub4dc \ud1b5\ud569\uc774 \uc644\ub8cc\ub418\uba74 \uacc4\uc88c, \uc800\ub110 \uae30\ub85d, \uac70\ub798, \uc608\uce21\uc774 \uc5ec\uae30\uc5d0 \ud45c\uc2dc\ub429\ub2c8\ub2e4.',
  },
  health: {
    eyebrow: '\ub3c4\uba54\uc778',
    title: '\uac74\uac15',
    subtitle: '\uc0dd\uccb4\uc9c0\ud45c, \uc6b4\ub3d9, \uc601\uc591. \ub0b4 \ubab8\uc758 \ud750\ub984\uc744 \uae30\ub85d\ud569\ub2c8\ub2e4.',
    comingSoonTitle: '\uac74\uac15 \ub3c4\uba54\uc778 \uace7 \ucd9c\uc2dc',
    comingSoonBody: '\ud504\ub860\ud2b8\uc5d4\ub4dc \ud1b5\ud569\uc774 \uc644\ub8cc\ub418\uba74 \uc0dd\uccb4\uc9c0\ud45c, \uc6b4\ub3d9 \uae30\ub85d, \uc601\uc591 \ucd94\uc801\uc774 \uc5ec\uae30\uc5d0 \ud45c\uc2dc\ub429\ub2c8\ub2e4.',
  },
  habits: {
    eyebrow: '\ub514\uc2dc\ud50c\ub9b0',
    title: '\uc2b5\uad00',
    subtitle: '\ud558\ub8e8\ud558\ub8e8\uc758 \uc2b5\uad00\uc744 \ucd94\uc801\ud558\uc5ec \uc9c8\uc758 \ub370\uc774\ud130\ub97c \uc30d\uc73c\uc138\uc694.',
    newHabit: '\uc0c8 \uc2b5\uad00',
    cancel: '\ucde8\uc18c',
    name: '\uc774\ub984',
    namePlaceholder: '\uc608: \uc544\uce68 \ub7ec\ub2dd',
    schedule: '\uc77c\uc815',
    daily: '\ub9e4\uc77c',
    weekly: '\ub9e4\uc8fc',
    custom: '\ucee4\uc2a4\ud140',
    description: '\uc124\uba85',
    optional: '\uc120\ud0dd\uc0ac\ud56d',
    creating: '\uc0dd\uc131 \uc911\u2026',
    createHabit: '\uc2b5\uad00 \ub9cc\ub4e4\uae30',
    yourHabits: '\ub0b4 \uc2b5\uad00',
    noHabits: '\uc544\uc9c1 \uc2b5\uad00\uc774 \uc5c6\uc2b5\ub2c8\ub2e4. \uc704\uc5d0\uc11c \uccab \uc2b5\uad00\uc744 \ub9cc\ub4dc\uc138\uc694.',
    log: '\uae30\ub85d',
    logged: '\uae30\ub85d\ub428',
    done: '\uc644\ub8cc',
    today: '\uc624\ub298',
    yesterday: '\uc5b4\uc81c',
    daysAgo: '\uc77c \uc804',
    dayStreak: '\uc77c \uc5f0\uc18d',
    undo: '\ucde8\uc18c',
    thisMonth: '\uc774\ubc88 \ub2ec',
    emptyTitle: '\ub9ac\ub4ec\uc744 \ub9cc\ub4e4\uc5b4 \ubcf4\uc138\uc694',
    emptyBody: '\uc791\uace0 \uafb8\uc900\ud55c \ud589\ub3d9\uc774 \uc758\ubbf8 \uc788\ub294 \ubcc0\ud654\ub97c \ub9cc\ub4ed\ub2c8\ub2e4. \uccab \uc2b5\uad00\uc744 \ub9cc\ub4e4\uace0 \uc5f0\uc18d \uae30\ub85d\uc744 \uc2dc\uc791\ud558\uc138\uc694.',
    emptyAction: '\uccab \uc2b5\uad00 \ub9cc\ub4e4\uae30',
    deleteTitle: '\uc2b5\uad00\uc744 \uc0ad\uc81c\ud560\uae4c\uc694?',
    deleteBody: '{name}\uacfc(\uc640) \ubaa8\ub4e0 \uae30\ub85d\uc774 \uc601\uad6c\uc801\uc73c\ub85c \uc0ad\uc81c\ub429\ub2c8\ub2e4. \uc774 \uc791\uc5c5\uc740 \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.',
    deleteConfirm: '\uc0ad\uc81c',
    deleteCancel: '\ucde8\uc18c',
    detailTitle: '\uc2b5\uad00 \uc0c1\uc138',
    currentStreak: '\ud604\uc7ac \uc5f0\uc18d',
    longestStreak: '\ucd5c\uc7a5 \uc5f0\uc18d',
    completionRate: '\uc644\ub8cc\uc728',
    totalLogs: '\ucd1d \uae30\ub85d',
    last30Days: '\ucd5c\uadfc 30\uc77c',
    yearlyHeatmap: '\uc5f0\uac04 \ud788\ud2b8\ub9f5',
    selectHabit: '\uc2b5\uad00\uc744 \uc120\ud0dd\ud558\uba74 \ubd84\uc11d\uc744 \ubcfc \uc218 \uc788\uc2b5\ub2c8\ub2e4',
    days: '\uc77c',
    noData: '\ub370\uc774\ud130 \uc5c6\uc74c',
    dueIn: '{time} 후 예정',
    dueSoon: '곧 예정',
    overdue: '{time} 지남',
  },
  skills: {
    eyebrow: '\ub9c8\uc2a4\ud130\ub9ac',
    title: '\uc2a4\ud0ac',
    subtitle: '\uc2a4\ud0ac\uacfc \uc5f0\uc2b5 \uc138\uc158\uc744 \ucd94\uc801\ud558\uc5ec \uc9c8\uc758 \ubd84\uc11d\uc5d0 \ud65c\uc6a9\ud558\uc138\uc694.',
    newSkill: '\uc0c8 \uc2a4\ud0ac',
    cancel: '\ucde8\uc18c',
    name: '\uc774\ub984',
    namePlaceholder: '\uc608: \ud53c\uc544\ub178',
    category: '\uce74\ud14c\uace0\ub9ac',
    categoryPlaceholder: '\uc608: \uc74c\uc545',
    description: '\uc124\uba85',
    optional: '\uc120\ud0dd\uc0ac\ud56d',
    creating: '\uc0dd\uc131 \uc911\u2026',
    createSkill: '\uc2a4\ud0ac \ub9cc\ub4e4\uae30',
    logPractice: '\uc5f0\uc2b5 \uae30\ub85d',
    durationLabel: '\uc2dc\uac04 (\ubd84)',
    notes: '\uba54\ubaa8',
    logging: '\uae30\ub85d \uc911\u2026',
    logSession: '\uc138\uc158 \uae30\ub85d',
    yourSkills: '\ub0b4 \uc2a4\ud0ac',
    noSkills: '\uc544\uc9c1 \uc2a4\ud0ac\uc774 \uc5c6\uc2b5\ub2c8\ub2e4. \uc704\uc5d0\uc11c \uccab \uc2a4\ud0ac\uc744 \ub9cc\ub4dc\uc138\uc694.',
    practice: '\uc5f0\uc2b5',
    sessions: '\ud68c',
    sessionsLabel: '\uc138\uc158',
    hoursLabel: '\uc2dc\uac04',
    milestonesLabel: '\ub9c8\uc77c\uc2a4\ud1a4',
    minuteShort: '\ubd84',
    hourShort: '\uc2dc\uac04',
    weekShort: '\uc8fc',
    streak: '\uc77c \uc5f0\uc18d',
    summaryTotalHours: '\ucd1d \uc2dc\uac04',
    summarySessions: '\uc138\uc158',
    summaryAtRisk: '\uc8fc\uc758 \ud544\uc694',
    summaryActive: '\ud65c\uc131',
    migrationNoticeTitle: '\ub9c8\uc774\uadf8\ub808\uc774\uc158 \uc548\ub0b4',
    migrationNoticeBody: '\uae30\uc874 \uc2a4\ud0ac\uc740 \uc548\uc804\ud55c \uae30\ubcf8\uac12\uc73c\ub85c \uc720\uc9c0\ub429\ub2c8\ub2e4. \uac01 \uc2a4\ud0ac \uacbd\ub85c\uc5d0\uc11c \ubaa9\ud45c \uc885\uc810\uc744 \uc870\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.',
    stepOf2: '{step}\ub2e8\uacc4 / 2',
    skillBasics: '\uc2a4\ud0ac \uae30\ubcf8',
    goalEndpoint: '\ubaa9\ud45c \uc885\uc810',
    rolloutGateTitle: '\ub864\uc544\uc6c3 \uac8c\uc774\ud2b8',
    rolloutGateBody: '\uc774 \ub864\uc544\uc6c3\uc5d0\uc11c\ub294 \uc0c8 \uc2a4\ud0ac\uc5d0 \ubaa9\ud45c\uac00 \ud544\uc218\uc785\ub2c8\ub2e4. \uc2a4\ud0ac\uc744 \ub9cc\ub4e4\uae30 \uc804\uc5d0 \ubaa9\ud45c \uc720\ud615\uacfc \uac12\uc744 \uc120\ud0dd\ud558\uc138\uc694.',
    continueAction: '\uacc4\uc18d',
    back: '\ub4a4\ub85c',
    goalType: '\ubaa9\ud45c \uc720\ud615',
    targetValue: '\ubaa9\ud45c \uac12',
    quickPresets: '\ube60\ub978 \uc124\uc815',
    skillPreview: '\uc2e4\uc2dc\uac04 \ubbf8\ub9ac\ubcf4\uae30',
    preview: '\ubbf8\ub9ac\ubcf4\uae30',
    goalTypeLabel: '\ubaa9\ud45c \uc720\ud615',
    creationSnapshot: '\uc0dd\uc131 \uc2a4\ub0c5\uc0f7',
    creationSnapshotBody: '\uc774 \uc2a4\ud0ac\uc740 \uae30\ubcf8 \uae30\uc900\uc120\uc73c\ub85c \uc2dc\uc791\ud558\uace0, \ubaa9\ud45c \uc885\uc810\uc744 \uc124\uc815\ud558\uba74 \uc608\uce21 \uc900\ube44\uac00 \ub429\ub2c8\ub2e4.',
    studioHeading: '\uc2e4\uc81c\ub85c \uc720\uc9c0\ud560 \uc218 \uc788\ub294 \uc5f0\uc2b5 \ub9ac\ub4ec\uc744 \ub9cc\ub4e4\uace0 \uc788\uc5b4\uc694.',
    signalClearSkillName: '\uba85\ud655\ud55c \uc2a4\ud0ac \uc774\ub984',
    signalCategoryContextAdded: '\uce74\ud14c\uace0\ub9ac \ub9e5\ub77d \ucd94\uac00',
    signalGoalEndpointSelected: '\ubaa9\ud45c \uc885\uc810 \uc120\ud0dd',
    signalDescriptionIncludesIntent: '\uc124\uba85\uc5d0 \uc758\ub3c4 \ud3ec\ud568',
    tipNameSkillFirst: '\uba3c\uc800 \uc2a4\ud0ac \uc774\ub984\uc744 \uc815\ud558\uba74 \uacc4\ud68d\uc774 \ub354 \uad6c\uccb4\uc801\uc73c\ub85c \ub290\uaef4\uc9d1\ub2c8\ub2e4.',
    tipGoalOptional: '\uc9c0\uae08\uc740 \ubaa9\ud45c\ub97c \ube44\uc6cc\ub450\uace0 \ub098\uc911\uc5d0 {editGoal}\uc5d0\uc11c \uc124\uc815\ud574\ub3c4 \ub429\ub2c8\ub2e4.',
    tipStrongEndpointSet: '\uc88b\uc740 \ubaa9\ud45c\uac00 \uc124\uc815\ub418\uc5c8\uc5b4\uc694. \uacbd\ub85c \uac00\uc774\ub4dc\uc640 \uc608\uce21\uc758 \uae30\uc900\uc774 \ub354 \ubd84\uba85\ud574\uc9d1\ub2c8\ub2e4.',
    goalTypeHelpSessions: '\uc138\uc158\uc740 \uc77c\uad00\uc131 \ubaa9\ud45c\uc5d0 \uc88b\uc2b5\ub2c8\ub2e4. \ubaa9\ud45c \uac12\uc740 \uae30\ub85d\ud560 \uc5f0\uc2b5 \uc138\uc158 \uc218\uc785\ub2c8\ub2e4.',
    goalTypeHelpHours: '\uc2dc\uac04\uc740 \ucd1d\ub7c9 \ubaa9\ud45c\uc5d0 \uc88b\uc2b5\ub2c8\ub2e4. \ubaa9\ud45c \uac12\uc740 \ub204\uc801\ud560 \ucd1d \uc2dc\uac04\uc785\ub2c8\ub2e4.',
    goalTypeHelpMilestones: '\ub9c8\uc77c\uc2a4\ud1a4\uc740 \uc9c8\uc801 \uccb4\ud06c\ud3ec\uc778\ud2b8\uc5d0 \uc88b\uc2b5\ub2c8\ub2e4. \ubaa9\ud45c \uac12\uc740 \uc644\ub8cc\ud560 \ub9c8\uc77c\uc2a4\ud1a4 \uac1c\uc218\uc785\ub2c8\ub2e4.',
    unit: '\ub2e8\uc704',
    goalSnapshot: '\ubaa9\ud45c \uc2a4\ub0c5\uc0f7',
    doneSoFar: '\uae4c\uc9c0 \uc644\ub8cc',
    targetingTotal: '\ucd1d {target} \ubaa9\ud45c',
    pace: '\ud398\uc774\uc2a4',
    eta: '\uc608\uc0c1 \uc644\ub8cc\uc77c',
    notEnoughDataYet: '\ub370\uc774\ud130\uac00 \ub354 \ud544\uc694\ud569\ub2c8\ub2e4',
    notAvailableYet: '\uc544\uc9c1 \uc81c\uacf5\ub418\uc9c0 \uc54a\uc74c',
    milestoneQualitativeHint: '\ub9c8\uc77c\uc2a4\ud1a4 \ubaa9\ud45c\ub294 \uc9c8\uc801 \uac00\uc774\ub4dc\uc785\ub2c8\ub2e4. \uc9c4\ud589 \ubc29\ud5a5\uc744 \ud655\uc778\ud558\uace0 \ud575\uc2ec \uccb4\ud06c\ud3ec\uc778\ud2b8\ub97c \uc644\ub8cc\ud560 \ub54c\ub9c8\ub2e4 \uc5c5\ub370\uc774\ud2b8\ud558\uc138\uc694.',
    quickActions: '\ube60\ub978 \uc791\uc5c5',
    raiseTargetBy10: '\ubaa9\ud45c +10% \uc0c1\ud5a5',
    extendTimelineBy14d: '\uae30\ud55c +14\uc77c \uc5f0\uc7a5',
    deadlineOptional: '\uae30\ud55c(\uc120\ud0dd)',
    saveGoal: '\ubaa9\ud45c \uc800\uc7a5',
    saving: '\uc800\uc7a5 \uc911...',
    continuePracticeTitle: '\uc5f0\uc2b5 \uacc4\uc18d - {skill}',
    suggested: '\ucd94\ucc9c',
    practiceStep: '\uc5f0\uc2b5 \ub2e8\uacc4',
    auto: '\uc790\ub3d9',
    recommendedPrefix: '\ucd94\ucc9c: {step}',
    recommendedFallback: '\uacbd\ub85c \uc815\ubcf4\uac00 \ucda9\ubd84\ud574\uc9c0\uba74 \ucd94\ucc9c \ub2e8\uacc4\uac00 \ud45c\uc2dc\ub429\ub2c8\ub2e4.',
    pacingCue: '\ud398\uc774\uc2f1 \uc548\ub0b4',
    pacingCueBody: '\ucd94\ucc9c \uc2dc\uac04\uc740 \ucd5c\uadfc \ub9ac\ub4ec\uc5d0 \uae30\ubc18\ud569\ub2c8\ub2e4: \uc57d {minutes}\ubd84.',
    sessionSaved: '\uc138\uc158 \uc800\uc7a5\ub428',
    totalNowAround: '\ud604\uc7ac \ub204\uc801 \uc57d {total}.',
    nextUpPrefix: '\ub2e4\uc74c: {step}',
    nextRecommendedAction: '\ub2e4\uc74c \ucd94\ucc9c \uc791\uc5c5',
    setGoal: '\ubaa9\ud45c \uc124\uc815',
    editGoal: '\ubaa9\ud45c \uc218\uc815',
    continuePractice: '\uc5f0\uc2b5 \uacc4\uc18d',
    viewInsights: '\uc778\uc0ac\uc774\ud2b8 \ubcf4\uae30',
    insightsTitle: '\uc778\uc0ac\uc774\ud2b8 - {skill}',
    reviewGoalProgress: '\ubaa9\ud45c \uc9c4\ud589 \uac80\ud1a0',
    goalProgress: '\ubaa9\ud45c \uc9c4\ud589',
    nowLabel: '\ud604\uc7ac',
    nextLabel: '\ub2e4\uc74c',
    riskLabel: '\ub9ac\uc2a4\ud06c',
    nowTowardGoal: '\ubaa9\ud45c\uc758 {progress} \uc9c4\ud589\ud588\uc5b4\uc694.',
    nowPracticeVolume: '{sessions}\ud68c \uc138\uc158\uc5d0\uc11c {minutes} \uc5f0\uc2b5\ud588\uc5b4\uc694.',
    riskNone: '\ud604\uc7ac\ub294 \ud06c\uac8c \uc6b0\ub824\ub420 \uc2e0\ud638\uac00 \uc5c6\uc5b4\uc694.',
    riskNeedMoreHistory: '\uc548\uc815\uc801\uc778 \ub9ac\uc2a4\ud06c \uac00\uc774\ub4dc\ub97c \uc704\ud574 \uc774\ub825\uc774 \uc870\uae08 \ub354 \ud544\uc694\ud574\uc694.',
    density: '\ubc00\ub3c4',
    densityCompact: '\ucf64\ud329\ud2b8',
    densityComfortable: '\uc5ec\uc720',
    sortBy: '\uc815\ub82c',
    sortUrgency: '\uc6b0\uc120\uc21c\uc704',
    sortMomentum: '\ud750\ub984',
    sortAlphabetical: '\uac00\ub098\ub2e4\uc21c',
    needsAttention: '\uc9d1\uc911 \ud655\uc778 \ud544\uc694',
    attentionStalled: '\ud750\ub984 \uba48\ucda4',
    attentionBelowPace: '\ud398\uc774\uc2a4 \ubd80\uc871',
    attentionDeadlineRisk: '\uae30\ud55c \uc704\ud5d8',
    last7Days: '\uc9c0\ub09c 7\uc77c {count}\ud68c',
    weeklyCadence: '\uc8fc\uac04 \ub9ac\ub4ec',
    weeklyCadenceAria: '{name}\uc758 \uc8fc\uac04 \ub9ac\ub4ec',
    nextActionSetupGoalThenPractice: '\ub2e4\uc74c \uc81c\uc548: \uba3c\uc800 \ubaa9\ud45c \uc885\uc810\uc744 \uc815\ud55c \ub4a4 \uc5f0\uc2b5\uc744 \uc774\uc5b4\uac00\uba74 \uc88b\uc2b5\ub2c8\ub2e4.',
    nextActionKeepEndpointStable: '\ub2e4\uc74c \uc81c\uc548: \uc9c0\uae08\ucc98\ub7fc \uc5f0\uc2b5\uc744 \uc774\uc5b4\uac00\uba74 \uc774 \ubaa9\ud45c \uc885\uc810\uc744 \uc548\uc815\uc801\uc73c\ub85c \uc720\uc9c0\ud560 \uc218 \uc788\uc5b4\uc694.',
    nextActionRecoverMomentum: '\ub2e4\uc74c \uc81c\uc548: \uc624\ub298 \uc9e7\uc740 \uc138\uc158\uc744 \ud558\ub098 \uae30\ub85d\ud558\uba74 \ub9ac\ub4ec\uc744 \ub2e4\uc2dc \ub418\ucc3e\ub294 \ub370 \ub3c4\uc6c0\uc774 \ub429\ub2c8\ub2e4.',
    nextActionSustainRhythm: '\ub2e4\uc74c \uc81c\uc548: \uc774 \uc8fc\uc758 \ub9ac\ub4ec\uc744 \uc720\uc9c0\ud558\ub3c4\ub85d \uac19\uc740 \ud398\uc774\uc2a4\ub85c \uc5f0\uc2b5\uc744 \uc774\uc5b4\uac00\uba74 \uc88b\uc2b5\ub2c8\ub2e4.',
    nextActionFocusedSession: '\ub2e4\uc74c \uc81c\uc548: \uc624\ub298 \uc9d1\uc911 \uc138\uc158 \ud558\ub098\ub97c \ub354\ud558\uba74 \uc2a4\ud0ac \ud750\ub984\uc744 \uafb8\uc900\ud788 \uc774\uc5b4\uac08 \uc218 \uc788\uc5b4\uc694.',
    forecast: '\uc608\uce21 ({days}\uc77c)',
    projectedSummary: '\uc608\uce21 {minutes}, {sessions}\ud68c \uc138\uc158.',
    forecastScenarios: '\uc608\uce21 \uc2dc\ub098\ub9ac\uc624',
    scenarioKeepPace: '\ud604\uc7ac \ud398\uc774\uc2a4 \uc720\uc9c0',
    scenarioPlusOneSession: '\uc138\uc158 +1',
    scenarioPlusThirtyMinutes: '30\ubd84 \ucd94\uac00',
    scenarioProjectedProgress: '\uc2dc\ub098\ub9ac\uc624 \uae30\uc900 \uc608\uc0c1 \uc9c4\ud589: \ubaa9\ud45c\uc758 {progress}.',
    statusCompleted: '\uc644\ub8cc',
    statusAtRisk: '\uc8fc\uc758 \ud544\uc694',
    statusOnTrack: '\uc21c\uc870\ub86d\uac8c \uc9c4\ud589 \uc911',
    statusAhead: '\uc55e\uc11c\uac00\ub294 \uc911',
    errorGoalRequired: '\uc774 \ub864\uc544\uc6c3\uc5d0\uc11c\ub294 \ubaa9\ud45c \uc885\uc810\uc774 \ud544\uc218\uc785\ub2c8\ub2e4. \uacc4\uc18d\ud558\ub824\uba74 \ubaa9\ud45c\ub97c \uc124\uc815\ud558\uc138\uc694.',
    errorCreateFailed: '\uc2a4\ud0ac \uc0dd\uc131\uc5d0 \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4. \uc785\ub825\uac12\uc744 \ud655\uc778\ud55c \ub4a4 \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.',
    errorUpdateGoalFailed: '\ubaa9\ud45c \uc5c5\ub370\uc774\ud2b8\uc5d0 \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \uc8fc\uc138\uc694.',
    errorTargetValueRequired: '\ubaa9\ud45c \uac12\uc740 0\ubcf4\ub2e4 \ucee4\uc57c \ud569\ub2c8\ub2e4.',
    statusInsufficientData: '\ub370\uc774\ud130 \ubd80\uc871',
    forecastReasonCompleted: '\ud604\uc7ac \ucd94\uc138\ub85c\ub3c4 \uc774 \ubaa9\ud45c \uae30\uac04\uc744 \ucda9\uc871\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4.',
    forecastReasonNoGoalConfigured: '\uc544\uc9c1 \ubaa9\ud45c\uac00 \uc124\uc815\ub418\uc9c0 \uc54a\uc544 \uac00\uc774\ub4dc\uac00 \uc81c\ud55c\ub429\ub2c8\ub2e4.',
    forecastReasonNoRecentSessions: '\ucd5c\uadfc \ud65c\ub3d9\uc774 \uc801\uc5b4 \uc774\ubc88 \uc8fc \ubaa9\ud45c \ucd94\uc138\uac00 \ub290\uc2a8\ud574\uc9c8 \uc218 \uc788\uc2b5\ub2c8\ub2e4.',
    forecastReasonNeedsConsistency: '\ucd5c\uadfc \ud328\ud134\uc0c1 \ub354 \uc77c\uad00\ub41c \uc5f0\uc2b5\uc774 \ud544\uc694\ud569\ub2c8\ub2e4.',
    forecastReasonQualitativeGoal: '\uc774 \ubaa9\ud45c \uc720\ud615\uc740 \uc9c8\uc801\uc774\ubbc0\ub85c \uc218\uce58 \uc608\uce21 \ub300\uc2e0 \ud65c\ub3d9 \uac00\uc774\ub4dc\ub97c \uc81c\uacf5\ud569\ub2c8\ub2e4.',
    forecastReasonNeedMoreHistory: '\uc548\uc815\uc801\uc778 \uac00\uc774\ub4dc\ub97c \uc704\ud574 \ud65c\ub3d9 \uc774\ub825\uc774 \uc870\uae08 \ub354 \ud544\uc694\ud569\ub2c8\ub2e4.',
    forecastReasonOnTrack: '\ucd5c\uadfc \uc77c\uad00\uc131\uc73c\ub85c \ubcf4\uc544 \ud604\uc7ac \ud398\uc774\uc2a4\ub97c \uc720\uc9c0\ud558\uae30 \uc88b\uc2b5\ub2c8\ub2e4.',
    celebrationSummary: '+{minutes}\ubd84, +{sessions}\ud68c \uc138\uc158, \uc5f0\uc18d \uac12 +{streak}.',
    deleteTitle: '\uc2a4\ud0ac\uc744 \uc0ad\uc81c\ud560\uae4c\uc694?',
    deleteBody: '{name}\uacfc(\uc640) \ubaa8\ub4e0 \uc5f0\uc2b5 \uae30\ub85d\uc774 \uc601\uad6c\uc801\uc73c\ub85c \uc0ad\uc81c\ub429\ub2c8\ub2e4. \uc774 \uc791\uc5c5\uc740 \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.',
    deleteConfirm: '\uc0ad\uc81c',
    deleteCancel: '\ucde8\uc18c',
  },
  projects: {
    title: '\ud504\ub85c\uc81d\ud2b8',
    subtitle: '\uc9c8\uc758 \ubd84\uc11d\uc744 \uc704\ud55c \ud504\ub85c\uc81d\ud2b8\uc640 \ud0dc\uc2a4\ud06c\ub97c \uad00\ub9ac\ud558\uc138\uc694.',
    newProject: '\uc0c8 \ud504\ub85c\uc81d\ud2b8',
    cancel: '\ucde8\uc18c',
    createProject: '\ud504\ub85c\uc81d\ud2b8 \ub9cc\ub4e4\uae30',
    name: '\uc774\ub984',
    namePlaceholder: '\uc608: \uc6f9\uc0ac\uc774\ud2b8 \ub7f0\uce6d',
    targetDate: '\ubaa9\ud45c\uc77c',
    description: '\uc124\uba85',
    optional: '\uc120\ud0dd\uc0ac\ud56d',
    creating: '\uc0dd\uc131 \uc911\u2026',
    projects: '\ud504\ub85c\uc81d\ud2b8',
    loading: '\ub85c\ub529 \uc911\u2026',
    noProjects: '\uc544\uc9c1 \ud504\ub85c\uc81d\ud2b8\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \uc704\uc5d0\uc11c \ub9cc\ub4dc\uc138\uc694.',
    done: '\uc644\ub8cc',
    delete: '\uc0ad\uc81c',
    tasks: '\ud0dc\uc2a4\ud06c',
    addTask: '\ud0dc\uc2a4\ud06c \ucd94\uac00',
    taskTitleLabel: '\uc81c\ubaa9',
    taskTitlePlaceholder: '\ud0dc\uc2a4\ud06c \uc81c\ubaa9',
    taskNotes: '\uba54\ubaa8',
    adding: '\ucd94\uac00 \uc911\u2026',
    add: '\ucd94\uac00',
    noTasks: '\uc544\uc9c1 \ud0dc\uc2a4\ud06c\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.',
    complete: '\uc644\ub8cc',
  },
}

/* ═══════════════════════════════════════════════════════════════════════════
   Chinese (Simplified)
   ═══════════════════════════════════════════════════════════════════════════ */

const zh: AppTranslations = {
  login: {
    backToHome: '\u8fd4\u56de\u9996\u9875',
    welcomeBack: '\u6b22\u8fce\u56de\u6765',
    joinAlpha: '\u52a0\u5165\u5185\u6d4b',
    acceptInvite: '\u63a5\u53d7\u9080\u8bf7',
    signInSub: '\u767b\u5f55\u60a8\u7684\u6863\u6848\u5e93',
    registerSub: '\u5185\u6d4b\u9636\u6bb5 - \u9700\u8981\u9080\u8bf7\u7801',
    acceptInviteSub: '\u8bbe\u7f6e\u5bc6\u7801\u4ee5\u6fc0\u6d3b\u60a8\u7684\u8d26\u6237\uff0c\u7136\u540e\u76f4\u63a5\u8fdb\u5165\u65b0\u624b\u5f15\u5bfc\u3002',
    limitedSpots: '\u540d\u989d\u6709\u9650',
    email: '\u90ae\u7bb1',
    invitedEmail: '\u53d7\u9080\u90ae\u7bb1',
    password: '\u5bc6\u7801',
    confirmPassword: '\u786e\u8ba4\u5bc6\u7801',
    inviteToken: '\u9080\u8bf7\u7801',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: '\u8bf7\u8f93\u5165\u5bc6\u7801',
    confirmPasswordPlaceholder: '\u518d\u6b21\u8f93\u5165\u5bc6\u7801',
    invitePlaceholder: '\u7c98\u8d34\u60a8\u7684\u9080\u8bf7\u7801',
    pleaseWait: '\u8bf7\u7a0d\u5019\u2026',
    continue: '\u7ee7\u7eed',
    createAccount: '\u521b\u5efa\u8d26\u6237',
    finishSetup: '\u8bbe\u7f6e\u5bc6\u7801\u5e76\u7ee7\u7eed',
    finishSetupSignIn: '\u5bc6\u7801\u5df2\u8bbe\u7f6e\u5b8c\u6210\uff0c\u8bf7\u767b\u5f55\u540e\u7ee7\u7eed\u3002',
    passwordMismatch: '\u4e24\u6b21\u8f93\u5165\u7684\u5bc6\u7801\u4e0d\u4e00\u81f4\u3002',
    noAccount: '\u6ca1\u6709\u8d26\u6237\uff1f',
    register: '\u7acb\u5373\u6ce8\u518c',
    haveAccount: '\u5df2\u6709\u8d26\u6237\uff1f',
    signIn: '\u7acb\u5373\u767b\u5f55',
  },
  onboarding: {
    step1of2: '\u7b2c1\u6b65 / \u52722',
    step2of2: '\u7b2c2\u6b65 / \u52722',
    whatToTrack: '\u60a8\u60f3\u8ffd\u8e2a\u54ea\u4e9b\u9886\u57df\uff1f',
    whatToTrackSub: '\u9009\u62e9\u60a8\u5e0c\u671b\u6574\u7406\u7684\u751f\u6d3b\u9886\u57df\u3002',
    connectCalendar: '\u8fde\u63a5\u60a8\u7684\u65e5\u5386',
    connectCalendarSub: '\u5bfc\u5165\u65e5\u7a0b\uff0c\u8ba9 LifeOS \u7406\u89e3\u60a8\u7684\u65f6\u95f4\u3002',
    selected: '\u5df2\u9009\u62e9',
    back: '\u4e0a\u4e00\u6b65',
    continue: '\u7ee7\u7eed',
    saving: '\u4fdd\u5b58\u4e2d\u2026',
    errorDomain: '\u8bf7\u81f3\u5c11\u9009\u62e9\u4e00\u4e2a\u9886\u57df\u4ee5\u7ee7\u7eed',
    errorCalendar: '\u8bf7\u9009\u62e9\u4e00\u4e2a\u65e5\u5386\u9009\u9879\u4ee5\u7ee7\u7eed',
    errorGeneric: '\u51fa\u4e86\u70b9\u95ee\u9898\uff0c\u8bf7\u91cd\u8bd5\u3002',
    domains: [
      { id: 'finance', label: '\u8d22\u52a1', description: '\u8ffd\u8e2a\u652f\u51fa\u3001\u9884\u7b97\u4e0e\u76ee\u6807' },
      { id: 'health', label: '\u5065\u5eb7', description: '\u751f\u7406\u6307\u6807\u3001\u8fd0\u52a8\u4e0e\u8425\u517b' },
      { id: 'habits', label: '\u4e60\u60ef', description: '\u5efa\u7acb\u65e5\u5e38\u4e60\u60ef\uff0c\u8ffd\u8e2a\u8fde\u7eed\u8bb0\u5f55' },
      { id: 'skills', label: '\u6280\u80fd', description: '\u7ec3\u4e60\u8bb0\u5f55\u4e0e\u6210\u957f\u8f68\u8ff9' },
    ],
    calendar: [
      { id: 'google', label: 'Google \u65e5\u5386', subtitle: '\u540c\u6b65 Google Workspace \u65e5\u7a0b' },
      { id: 'apple', label: 'Apple \u65e5\u5386', subtitle: '\u540c\u6b65 iCloud \u65e5\u7a0b' },
      { id: 'skip', label: '\u6682\u65f6\u8df3\u8fc7', subtitle: '\u7a0d\u540e\u53ef\u4ee5\u8fde\u63a5\u65e5\u5386' },
    ],
    processing: {
      title: '\u6b63\u5728\u8046\u542c\u6863\u6848\u5e93...',
      subtitle: '\u6b63\u5728\u8fde\u63a5\u6570\u636e\u6d41...',
      complete: '\u5b8c\u6210',
      items: [
        { label: '\u4e60\u60ef\u6a21\u5f0f', status: '\u5df2\u53d1\u73b0' },
        { label: '\u6bcf\u5468\u8282\u5f8b', status: '\u5206\u6790\u4e2d' },
        { label: '\u4e13\u6ce8\u65f6\u6bb5', status: '\u6620\u5c04\u4e2d' },
        { label: '\u6210\u957f\u8f68\u8ff9', status: '\u5df2\u8fde\u63a5' },
      ],
      connected: '\u5df2\u8fde\u63a5',
      digitalRhythm: '\u6570\u5b57\u8282\u5f8b',
      digitalRhythmDesc: '\u4e0e\u60a8\u7684\u4e13\u6ce8\u5468\u671f\u548c\u81ea\u7136\u4f11\u606f\u65f6\u95f4\u5bf9\u9f50\u3002',
      processing: '\u5904\u7406\u4e2d',
      intentMapping: '\u610f\u56fe\u6620\u5c04',
      intentMappingDesc: '\u5c06\u65e5\u5fd7\u8f6c\u5316\u4e3a\u4e0b\u4e00\u7ae0\u7684\u53ef\u6267\u884c\u667a\u6167\u3002',
    },
  },
  header: {
    calendar: '\u65e5\u5386',
    inquiry: '\u95ee\u8be2',
    finances: '\u8d22\u52a1',
    health: '\u5065\u5eb7',
    habits: '\u4e60\u60ef',
    skills: '\u6280\u80fd',
    signOut: '\u9000\u51fa\u767b\u5f55',
  },
  footer: {
    tagline: '\u60a8\u7684\u4eba\u751f\uff0c\u6e05\u6670\u5448\u73b0\u3002',
    philosophy: '\u786e\u5b9a\u6027\u667a\u80fd \u00b7 \u65e0\u81ea\u4e3bML',
  },
  layout: {
    loading: '\u6b63\u5728\u6253\u5f00\u60a8\u7684\u5723\u6bbf\u2026',
  },
  calendar: {
    eyebrow: '\u65f6\u95f4\u7ebf',
    title: '\u65e5\u5386',
    subtitle: '\u7ba1\u7406\u65e5\u5386\u4e8b\u4ef6\uff0c\u7528\u4e8e\u95ee\u8be2\u5206\u6790',
    today: '\u4eca\u5929',
    year: '\u5e74',
    month: '\u6708',
    week: '\u5468',
    day: '\u65e5',
    weekdaySun: '\u65e5',
    weekdayMon: '\u4e00',
    weekdayTue: '\u4e8c',
    weekdayWed: '\u4e09',
    weekdayThu: '\u56db',
    weekdayFri: '\u4e94',
    weekdaySat: '\u516d',
    addEvent: '\u6dfb\u52a0\u4e8b\u4ef6',
    cancel: '\u53d6\u6d88',
    newEvent: '\u65b0\u5efa\u4e8b\u4ef6',
    titleLabel: '\u6807\u9898',
    titlePlaceholder: '\u4e8b\u4ef6\u6807\u9898',
    location: '\u5730\u70b9',
    optional: '\u9009\u586b',
    start: '\u5f00\u59cb',
    end: '\u7ed3\u675f',
    allDay: '\u5168\u5929',
    saving: '\u4fdd\u5b58\u4e2d\u2026',
    saveEvent: '\u4fdd\u5b58\u4e8b\u4ef6',
    events: '\u4e8b\u4ef6',
    noEvents: '\u6682\u65e0\u4e8b\u4ef6\uff0c\u5728\u4e0a\u65b9\u6dfb\u52a0\u60a8\u7684\u7b2c\u4e00\u4e2a\u4e8b\u4ef6',
  },
  finances: {
    eyebrow: '\u9886\u57df',
    title: '\u8d22\u52a1',
    subtitle: '\u8ffd\u8e2a\u652f\u51fa\u3001\u9884\u7b97\u4e0e\u76ee\u6807\u3002\u6e05\u6670\u8bb2\u8ff0\u60a8\u7684\u8d22\u52a1\u6545\u4e8b\u3002',
    comingSoonTitle: '\u8d22\u52a1\u6a21\u5757\u5373\u5c06\u4e0a\u7ebf',
    comingSoonBody: '\u524d\u7aef\u96c6\u6210\u5b8c\u6210\u540e\uff0c\u8d26\u6237\u3001\u65e5\u8bb0\u6761\u76ee\u3001\u4ea4\u6613\u8bb0\u5f55\u548c\u9884\u6d4b\u5c06\u5728\u6b64\u663e\u793a',
  },
  health: {
    eyebrow: '\u9886\u57df',
    title: '\u5065\u5eb7',
    subtitle: '\u751f\u7406\u6307\u6807\u3001\u8fd0\u52a8\u4e0e\u8425\u517b\u3002\u6e29\u67d4\u8bb0\u5f55\u60a8\u7684\u8eab\u5fc3\u72b6\u6001\u3002',
    comingSoonTitle: '\u5065\u5eb7\u6a21\u5757\u5373\u5c06\u4e0a\u7ebf',
    comingSoonBody: '\u524d\u7aef\u96c6\u6210\u5b8c\u6210\u540e\uff0c\u751f\u7406\u6307\u6807\u3001\u8fd0\u52a8\u8bb0\u5f55\u548c\u8425\u517b\u8ffd\u8e2a\u5c06\u5728\u6b64\u663e\u793a\u3002',
  },
  habits: {
    eyebrow: '\u81ea\u5f8b',
    title: '\u4e60\u60ef',
    subtitle: '\u8ffd\u8e2a\u6bcf\u65e5\u4e60\u60ef\uff0c\u79ef\u7d2f\u95ee\u8be2\u6570\u636e',
    newHabit: '\u65b0\u5efa\u4e60\u60ef',
    cancel: '\u53d6\u6d88',
    name: '\u540d\u79f0',
    namePlaceholder: '\u4f8b\u5982\uff1a\u6668\u8dd1',
    schedule: '\u5468\u671f',
    daily: '\u6bcf\u5929',
    weekly: '\u6bcf\u5468',
    custom: '\u81ea\u5b9a\u4e49',
    description: '\u63cf\u8ff0',
    optional: '\u9009\u586b',
    creating: '\u521b\u5efa\u4e2d\u2026',
    createHabit: '\u521b\u5efa\u4e60\u60ef',
    yourHabits: '\u6211\u7684\u4e60\u60ef',
    noHabits: '\u6682\u65e0\u4e60\u60ef\uff0c\u5728\u4e0a\u65b9\u521b\u5efa\u60a8\u7684\u7b2c\u4e00\u4e2a\u4e60\u60ef',
    log: '\u8bb0\u5f55',
    logged: '\u5df2\u8bb0\u5f55',
    done: '\u5b8c\u6210',
    today: '\u4eca\u5929',
    yesterday: '\u6628\u5929',
    daysAgo: '\u5929\u524d',
    dayStreak: '\u5929\u8fde\u7eed',
    undo: '\u64a4\u9500',
    thisMonth: '\u672c\u6708',
    emptyTitle: '\u5f00\u59cb\u57f9\u517b\u4f60\u7684\u8282\u594f',
    emptyBody: '\u5fae\u5c0f\u800c\u6301\u7eed\u7684\u884c\u52a8\u4f1a\u79ef\u7d2f\u6210\u6709\u610f\u4e49\u7684\u6539\u53d8\u3002\u521b\u5efa\u4f60\u7684\u7b2c\u4e00\u4e2a\u4e60\u60ef\uff0c\u8ba9\u8fde\u7eed\u8bb0\u5f55\u8bb2\u8ff0\u6545\u4e8b\u3002',
    emptyAction: '\u521b\u5efa\u7b2c\u4e00\u4e2a\u4e60\u60ef',
    deleteTitle: '\u5220\u9664\u4e60\u60ef\uff1f',
    deleteBody: '\u8fd9\u5c06\u6c38\u4e45\u5220\u9664 {name} \u53ca\u5176\u6240\u6709\u8bb0\u5f55\u3002\u6b64\u64cd\u4f5c\u65e0\u6cd5\u64a4\u9500\u3002',
    deleteConfirm: '\u5220\u9664',
    deleteCancel: '\u53d6\u6d88',
    detailTitle: '\u4e60\u60ef\u8be6\u60c5',
    currentStreak: '\u5f53\u524d\u8fde\u7eed',
    longestStreak: '\u6700\u957f\u8fde\u7eed',
    completionRate: '\u5b8c\u6210\u7387',
    totalLogs: '\u603b\u8bb0\u5f55',
    last30Days: '\u8fd1 30 \u5929',
    yearlyHeatmap: '\u5e74\u5ea6\u70ed\u529b\u56fe',
    selectHabit: '\u9009\u62e9\u4e00\u4e2a\u4e60\u60ef\u67e5\u770b\u5206\u6790',
    days: '\u5929',
    noData: '\u6682\u65e0\u6570\u636e',
    dueIn: '{time} 后到期',
    dueSoon: '即将到期',
    overdue: '已逾期 {time}',
  },
  skills: {
    eyebrow: '\u7cbe\u8fdb',
    title: '\u6280\u80fd',
    subtitle: '\u8ffd\u8e2a\u6280\u80fd\u4e0e\u7ec3\u4e60\u8bb0\u5f55\uff0c\u7528\u4e8e\u95ee\u8be2\u5206\u6790',
    newSkill: '\u65b0\u5efa\u6280\u80fd',
    cancel: '\u53d6\u6d88',
    name: '\u540d\u79f0',
    namePlaceholder: '\u4f8b\u5982\uff1a\u94a2\u7434',
    category: '\u5206\u7c7b',
    categoryPlaceholder: '\u4f8b\u5982\uff1a\u97f3\u4e50',
    description: '\u63cf\u8ff0',
    optional: '\u9009\u586b',
    creating: '\u521b\u5efa\u4e2d\u2026',
    createSkill: '\u521b\u5efa\u6280\u80fd',
    logPractice: '\u8bb0\u5f55\u7ec3\u4e60',
    durationLabel: '\u65f6\u957f\uff08\u5206\u949f\uff09',
    notes: '\u5907\u6ce8',
    logging: '\u8bb0\u5f55\u4e2d\u2026',
    logSession: '\u8bb0\u5f55\u7ec3\u4e60',
    yourSkills: '\u6211\u7684\u6280\u80fd',
    noSkills: '\u6682\u65e0\u6280\u80fd\uff0c\u5728\u4e0a\u65b9\u521b\u5efa\u60a8\u7684\u7b2c\u4e00\u4e2a\u6280\u80fd',
    practice: '\u7ec3\u4e60',
    sessions: '\u6b21',
    sessionsLabel: '\u573a\u6b21',
    hoursLabel: '\u5c0f\u65f6',
    milestonesLabel: '\u91cc\u7a0b\u7891',
    minuteShort: '\u5206',
    hourShort: '\u5c0f\u65f6',
    weekShort: '\u5468',
    streak: '\u5929\u8fde\u7eed',
    summaryTotalHours: '\u603b\u65f6\u957f',
    summarySessions: '\u7ec3\u4e60\u6b21\u6570',
    summaryAtRisk: '\u9700\u5173\u6ce8',
    summaryActive: '\u8fdb\u884c\u4e2d',
    migrationNoticeTitle: '\u8fc1\u79fb\u63d0\u793a',
    migrationNoticeBody: '\u5df2\u4fdd\u7559\u73b0\u6709\u6280\u80fd\u5e76\u5e94\u7528\u5b89\u5168\u9ed8\u8ba4\u503c\u3002\u60a8\u53ef\u4ee5\u5728\u6bcf\u4e2a\u6280\u80fd\u8def\u5f84\u4e2d\u8c03\u6574\u76ee\u6807\u7ec8\u70b9\u3002',
    stepOf2: '\u7b2c {step} \u6b65 / 2',
    skillBasics: '\u6280\u80fd\u57fa\u7840',
    goalEndpoint: '\u76ee\u6807\u7ec8\u70b9',
    rolloutGateTitle: '\u5206\u9636\u6bb5\u95e8\u63a7',
    rolloutGateBody: '\u5728\u5f53\u524d\u5206\u9636\u6bb5\u4e2d\uff0c\u65b0\u5efa\u6280\u80fd\u9700\u8981\u76ee\u6807\u3002\u8bf7\u5148\u9009\u62e9\u76ee\u6807\u7c7b\u578b\u548c\u76ee\u6807\u503c\u3002',
    continueAction: '\u7ee7\u7eed',
    back: '\u8fd4\u56de',
    goalType: '\u76ee\u6807\u7c7b\u578b',
    targetValue: '\u76ee\u6807\u503c',
    quickPresets: '\u5feb\u6377\u9884\u8bbe',
    skillPreview: '\u5b9e\u65f6\u9884\u89c8',
    preview: '\u9884\u89c8',
    goalTypeLabel: '\u76ee\u6807\u7c7b\u578b',
    creationSnapshot: '\u521b\u5efa\u6982\u89c8',
    creationSnapshotBody: '\u8be5\u6280\u80fd\u5c06\u4ee5\u5e72\u51c0\u57fa\u7ebf\u5f00\u59cb\uff0c\u8bbe\u5b9a\u76ee\u6807\u7ec8\u70b9\u540e\u5373\u53ef\u8fdb\u5165\u9884\u6d4b\u6a21\u5f0f\u3002',
    studioHeading: '\u60a8\u6b63\u5728\u6253\u9020\u4e00\u4e2a\u771f\u6b63\u80fd\u575a\u6301\u7684\u7ec3\u4e60\u8282\u594f\u3002',
    signalClearSkillName: '\u6e05\u6670\u7684\u6280\u80fd\u540d\u79f0',
    signalCategoryContextAdded: '\u5df2\u8865\u5145\u5206\u7c7b\u80cc\u666f',
    signalGoalEndpointSelected: '\u5df2\u9009\u62e9\u76ee\u6807\u7ec8\u70b9',
    signalDescriptionIncludesIntent: '\u63cf\u8ff0\u5305\u542b\u7ec3\u4e60\u610f\u56fe',
    tipNameSkillFirst: '\u5148\u547d\u540d\u8be5\u6280\u80fd\uff0c\u60a8\u7684\u8ba1\u5212\u4f1a\u66f4\u5177\u4f53\u4e5f\u66f4\u5bb9\u6613\u56de\u5230\u6b63\u8f68\u3002',
    tipGoalOptional: '\u76ee\u524d\u53ef\u4ee5\u4e0d\u586b\u76ee\u6807\uff0c\u7a0d\u540e\u5728 {editGoal} \u4e2d\u8865\u5145\u5373\u53ef\u3002',
    tipStrongEndpointSet: '\u76ee\u6807\u8bbe\u7f6e\u5f88\u597d\uff0c\u53ef\u4e3a\u8def\u5f84\u5f15\u5bfc\u548c\u9884\u6d4b\u63d0\u4f9b\u66f4\u6e05\u6670\u7684\u57fa\u7ebf\u3002',
    goalTypeHelpSessions: '\u9009\u62e9\u201c\u6b21\u6570\u201d\u9002\u5408\u4e00\u81f4\u6027\u76ee\u6807\u3002\u76ee\u6807\u503c\u8868\u793a\u60a8\u60f3\u8bb0\u5f55\u7684\u7ec3\u4e60\u6b21\u6570\u3002',
    goalTypeHelpHours: '\u9009\u62e9\u201c\u5c0f\u65f6\u201d\u9002\u5408\u603b\u91cf\u76ee\u6807\u3002\u76ee\u6807\u503c\u8868\u793a\u60a8\u60f3\u7d2f\u8ba1\u7684\u603b\u5c0f\u65f6\u6570\u3002',
    goalTypeHelpMilestones: '\u9009\u62e9\u201c\u91cc\u7a0b\u7891\u201d\u9002\u5408\u5b9a\u6027\u68c0\u67e5\u70b9\u3002\u76ee\u6807\u503c\u8868\u793a\u60a8\u60f3\u5b8c\u6210\u7684\u91cc\u7a0b\u7891\u6570\u91cf\u3002',
    unit: '\u5355\u4f4d',
    goalSnapshot: '\u76ee\u6807\u5feb\u7167',
    doneSoFar: '\u5df2\u5b8c\u6210',
    targetingTotal: '\u76ee\u6807\u603b\u8ba1 {target}\u3002',
    pace: '\u8282\u594f',
    eta: '\u9884\u8ba1\u5b8c\u6210\u65e5',
    notEnoughDataYet: '\u6570\u636e\u4e0d\u8db3',
    notAvailableYet: '\u6682\u4e0d\u53ef\u7528',
    milestoneQualitativeHint: '\u91cc\u7a0b\u7891\u76ee\u6807\u5c5e\u4e8e\u5b9a\u6027\u6307\u5f15\u3002\u8bf7\u5c06\u8be5\u6570\u503c\u4f5c\u4e3a\u65b9\u5411\u53c2\u8003\uff0c\u5e76\u5728\u5b8c\u6210\u5173\u952e\u8282\u70b9\u65f6\u66f4\u65b0\u3002',
    quickActions: '\u5feb\u6377\u64cd\u4f5c',
    raiseTargetBy10: '\u76ee\u6807 +10%',
    extendTimelineBy14d: '\u671f\u9650 +14\u5929',
    deadlineOptional: '\u622a\u6b62\u65e5\uff08\u53ef\u9009\uff09',
    saveGoal: '\u4fdd\u5b58\u76ee\u6807',
    saving: '\u4fdd\u5b58\u4e2d...',
    continuePracticeTitle: '\u7ee7\u7eed\u7ec3\u4e60 - {skill}',
    suggested: '\u5efa\u8bae',
    practiceStep: '\u7ec3\u4e60\u6b65\u9aa4',
    auto: '\u81ea\u52a8',
    recommendedPrefix: '\u63a8\u8350\uff1a{step}',
    recommendedFallback: '\u5f53\u8def\u5f84\u4e0a\u4e0b\u6587\u8db3\u591f\u65f6\uff0c\u5c06\u663e\u793a\u63a8\u8350\u6b65\u9aa4\u3002',
    pacingCue: '\u8282\u594f\u63d0\u793a',
    pacingCueBody: '\u5efa\u8bae\u65f6\u957f\u57fa\u4e8e\u60a8\u8fd1\u671f\u8282\u594f\uff1a\u7ea6 {minutes} \u5206\u949f\u3002',
    sessionSaved: '\u5df2\u4fdd\u5b58\u672c\u6b21\u7ec3\u4e60',
    totalNowAround: '\u5f53\u524d\u603b\u91cf\u7ea6 {total}\u3002',
    nextUpPrefix: '\u4e0b\u4e00\u6b65\uff1a{step}',
    nextRecommendedAction: '\u4e0b\u4e00\u4e2a\u63a8\u8350\u52a8\u4f5c',
    setGoal: '\u8bbe\u5b9a\u76ee\u6807',
    editGoal: '\u7f16\u8f91\u76ee\u6807',
    continuePractice: '\u7ee7\u7eed\u7ec3\u4e60',
    viewInsights: '\u67e5\u770b\u6d1e\u5bdf',
    insightsTitle: '\u6d1e\u5bdf - {skill}',
    reviewGoalProgress: '\u68c0\u89c6\u76ee\u6807\u8fdb\u5ea6',
    goalProgress: '\u76ee\u6807\u8fdb\u5ea6',
    nowLabel: '\u5f53\u524d',
    nextLabel: '\u4e0b\u4e00\u6b65',
    riskLabel: '\u98ce\u9669',
    nowTowardGoal: '\u5df2\u8fbe\u5230\u76ee\u6807\u7684 {progress}\u3002',
    nowPracticeVolume: '\u5df2\u7ec3\u4e60 {minutes}\uff0c\u5171 {sessions} \u6b21\u3002',
    riskNone: '\u6682\u65e0\u660e\u663e\u98ce\u9669\u4fe1\u53f7\u3002',
    riskNeedMoreHistory: '\u9700\u8981\u518d\u79ef\u7d2f\u4e00\u4e9b\u5386\u53f2\u6570\u636e\uff0c\u624d\u80fd\u7ed9\u51fa\u66f4\u7a33\u5b9a\u7684\u98ce\u9669\u6307\u5f15\u3002',
    density: '\u4fe1\u606f\u5bc6\u5ea6',
    densityCompact: '\u7d27\u51d1',
    densityComfortable: '\u8212\u9002',
    sortBy: '\u6392\u5e8f',
    sortUrgency: '\u7d27\u6025\u5ea6',
    sortMomentum: '\u52a8\u80fd',
    sortAlphabetical: '\u6309\u540d\u79f0',
    needsAttention: '\u9700\u4f18\u5148\u5173\u6ce8',
    attentionStalled: '\u8282\u594f\u505c\u6ede',
    attentionBelowPace: '\u4f4e\u4e8e\u8282\u594f',
    attentionDeadlineRisk: '\u622a\u6b62\u98ce\u9669',
    last7Days: '\u8fd17\u5929 {count}\u6b21',
    weeklyCadence: '\u6bcf\u5468\u8282\u594f',
    weeklyCadenceAria: '{name} \u7684\u6bcf\u5468\u8282\u594f',
    nextActionSetupGoalThenPractice: '\u4e0b\u4e00\u6b65\u5efa\u8bae\uff1a\u5148\u786e\u5b9a\u76ee\u6807\u7ec8\u70b9\uff0c\u518d\u7ee7\u7eed\u7ec3\u4e60\uff0c\u8282\u594f\u4f1a\u66f4\u7a33\u3002',
    nextActionKeepEndpointStable: '\u4e0b\u4e00\u6b65\u5efa\u8bae\uff1a\u6309\u5f53\u524d\u8282\u594f\u7ee7\u7eed\u7ec3\u4e60\uff0c\u6709\u52a9\u4e8e\u7a33\u5b9a\u5b88\u4f4f\u8fd9\u4e2a\u76ee\u6807\u3002',
    nextActionRecoverMomentum: '\u4e0b\u4e00\u6b65\u5efa\u8bae\uff1a\u4eca\u5929\u5148\u5b8c\u6210\u4e00\u6b21\u77ed\u7ec3\u4e60\uff0c\u53ef\u4ee5\u5e2e\u4f60\u5c3d\u5feb\u627e\u56de\u8282\u594f\u3002',
    nextActionSustainRhythm: '\u4e0b\u4e00\u6b65\u5efa\u8bae\uff1a\u4fdd\u6301\u8fd9\u5468\u7684\u7ec3\u4e60\u8282\u594f\uff0c\u7a33\u5b9a\u63a8\u8fdb\u5c31\u5f88\u597d\u3002',
    nextActionFocusedSession: '\u4e0b\u4e00\u6b65\u5efa\u8bae\uff1a\u4eca\u5929\u518d\u8865\u4e00\u6b21\u4e13\u6ce8\u7ec3\u4e60\uff0c\u8fd9\u9879\u6280\u80fd\u4f1a\u7ee7\u7eed\u5f80\u524d\u8d70\u3002',
    forecast: '\u9884\u6d4b\uff08{days}\u5929\uff09',
    projectedSummary: '\u9884\u8ba1 {minutes}\uff0c{sessions} \u6b21\u7ec3\u4e60\u3002',
    forecastScenarios: '\u9884\u6d4b\u60c5\u666f',
    scenarioKeepPace: '\u4fdd\u6301\u5f53\u524d\u8282\u594f',
    scenarioPlusOneSession: '\u518d\u52a0 1 \u6b21\u7ec3\u4e60',
    scenarioPlusThirtyMinutes: '\u518d\u52a0 30 \u5206\u949f',
    scenarioProjectedProgress: '\u5728\u8be5\u60c5\u666f\u4e0b\uff0c\u9884\u8ba1\u53ef\u8fbe\u5230\u76ee\u6807\u7684 {progress}\u3002',
    statusCompleted: '\u5df2\u5b8c\u6210',
    statusAtRisk: '\u9700\u5173\u6ce8',
    statusOnTrack: '\u8fdb\u5c55\u6b63\u5e38',
    statusAhead: '\u9886\u5148',
    errorGoalRequired: '\u5728\u5f53\u524d\u5206\u9636\u6bb5\u4e2d\uff0c\u76ee\u6807\u7ec8\u70b9\u662f\u5fc5\u586b\u9879\u3002\u8bf7\u8bbe\u7f6e\u76ee\u6807\u540e\u518d\u7ee7\u7eed\u3002',
    errorCreateFailed: '\u521b\u5efa\u6280\u80fd\u5931\u8d25\u3002\u8bf7\u68c0\u67e5\u8f93\u5165\u540e\u91cd\u8bd5\u3002',
    errorUpdateGoalFailed: '\u66f4\u65b0\u76ee\u6807\u5931\u8d25\u3002\u8bf7\u91cd\u8bd5\u3002',
    errorTargetValueRequired: '\u76ee\u6807\u503c\u5fc5\u987b\u5927\u4e8e 0\u3002',
    statusInsufficientData: '\u6570\u636e\u4e0d\u8db3',
    forecastReasonCompleted: '\u6309\u5f53\u524d\u8d8b\u52bf\uff0c\u60a8\u5df2\u80fd\u6ee1\u8db3\u8fd9\u4e2a\u76ee\u6807\u65f6\u7a97\u3002',
    forecastReasonNoGoalConfigured: '\u5c1a\u672a\u8bbe\u7f6e\u76ee\u6807\uff0c\u56e0\u6b64\u6307\u5f15\u6709\u9650\u3002',
    forecastReasonNoRecentSessions: '\u8fd1\u671f\u6d3b\u52a8\u8f83\u4f4e\uff0c\u672c\u5468\u76ee\u6807\u8fdb\u5ea6\u53ef\u80fd\u4e0b\u6ed1\u3002',
    forecastReasonNeedsConsistency: '\u8fd1\u671f\u6a21\u5f0f\u8868\u660e\u8fd9\u4e2a\u76ee\u6807\u9700\u8981\u66f4\u591a\u7a33\u5b9a\u6027\u3002',
    forecastReasonQualitativeGoal: '\u8be5\u76ee\u6807\u7c7b\u578b\u4e3a\u5b9a\u6027\u76ee\u6807\uff0c\u56e0\u6b64\u63d0\u4f9b\u6d3b\u52a8\u6307\u5f15\u800c\u975e\u6570\u503c\u9884\u6d4b\u3002',
    forecastReasonNeedMoreHistory: '\u9700\u8981\u66f4\u591a\u6d3b\u52a8\u5386\u53f2\u624d\u80fd\u751f\u6210\u7a33\u5b9a\u6307\u5f15\u3002',
    forecastReasonOnTrack: '\u8fd1\u671f\u4e00\u81f4\u6027\u8868\u660e\u60a8\u5f53\u524d\u8282\u594f\u53ef\u4ee5\u7a33\u5b9a\u7ef4\u6301\u3002',
    celebrationSummary: '+{minutes} \u5206\u949f\uff0c+{sessions} \u6b21\u7ec3\u4e60\uff0c\u8fde\u7eed\u503c +{streak}\u3002',
    deleteTitle: '\u5220\u9664\u6280\u80fd\uff1f',
    deleteBody: '\u8fd9\u5c06\u6c38\u4e45\u5220\u9664 {name} \u53ca\u5176\u6240\u6709\u7ec3\u4e60\u8bb0\u5f55\u3002\u6b64\u64cd\u4f5c\u65e0\u6cd5\u64a4\u9500\u3002',
    deleteConfirm: '\u5220\u9664',
    deleteCancel: '\u53d6\u6d88',
  },
  projects: {
    title: '\u9879\u76ee',
    subtitle: '\u7ba1\u7406\u9879\u76ee\u4e0e\u4efb\u52a1\uff0c\u7528\u4e8e\u95ee\u8be2\u5206\u6790',
    newProject: '\u65b0\u5efa\u9879\u76ee',
    cancel: '\u53d6\u6d88',
    createProject: '\u521b\u5efa\u9879\u76ee',
    name: '\u540d\u79f0',
    namePlaceholder: '\u4f8b\u5982\uff1a\u4e0a\u7ebf\u7f51\u7ad9',
    targetDate: '\u76ee\u6807\u65e5\u671f',
    description: '\u63cf\u8ff0',
    optional: '\u9009\u586b',
    creating: '\u521b\u5efa\u4e2d\u2026',
    projects: '\u9879\u76ee',
    loading: '\u52a0\u8f7d\u4e2d\u2026',
    noProjects: '\u6682\u65e0\u9879\u76ee\uff0c\u5728\u4e0a\u65b9\u521b\u5efa\u4e00\u4e2a',
    done: '\u5b8c\u6210',
    delete: '\u5220\u9664',
    tasks: '\u4efb\u52a1',
    addTask: '\u6dfb\u52a0\u4efb\u52a1',
    taskTitleLabel: '\u6807\u9898',
    taskTitlePlaceholder: '\u4efb\u52a1\u6807\u9898',
    taskNotes: '\u5907\u6ce8',
    adding: '\u6dfb\u52a0\u4e2d\u2026',
    add: '\u6dfb\u52a0',
    noTasks: '\u6682\u65e0\u4efb\u52a1',
    complete: '\u5b8c\u6210',
  },
}

/* ── Lookup ─────────────────────────────────────────────────────────────── */

export const appTranslations: Record<Lang, AppTranslations> = { en, zh, ko }

/**
 * Helper to get app translations for the current language.
 * Usage: const t = getAppTranslations(lang)
 */
export function getAppTranslations(lang: Lang): AppTranslations {
  return appTranslations[lang] ?? appTranslations.en
}
