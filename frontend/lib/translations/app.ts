import type { Lang } from '@/components/landing/translations'

/* ── Login page ─────────────────────────────────────────────────────────── */

export interface LoginTranslations {
  backToHome: string
  welcomeBack: string
  joinAlpha: string
  signInSub: string
  registerSub: string
  limitedSpots: string
  email: string
  password: string
  inviteToken: string
  emailPlaceholder: string
  passwordPlaceholder: string
  invitePlaceholder: string
  pleaseWait: string
  continue: string
  createAccount: string
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
  streak: string
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
    signInSub: 'Sign in to your archive.',
    registerSub: 'Private alpha \u2014 invite token required.',
    limitedSpots: 'Limited spots',
    email: 'Email',
    password: 'Password',
    inviteToken: 'Invite token',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: 'Enter password',
    invitePlaceholder: 'Paste your invite token',
    pleaseWait: 'Please wait\u2026',
    continue: 'Continue',
    createAccount: 'Create Account',
    noAccount: 'No account? ',
    register: 'Register',
    haveAccount: 'Have an account? ',
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
    streak: 'd streak',
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
    signInSub: '\uc544\uce74\uc774\ube0c\uc5d0 \ub85c\uadf8\uc778\ud558\uc138\uc694.',
    registerSub: '\ud504\ub77c\uc774\ube57 \uc54c\ud30c \u2014 \ucd08\ub300 \ud1a0\ud070\uc774 \ud544\uc694\ud569\ub2c8\ub2e4.',
    limitedSpots: '\uc778\uc6d0 \uc81c\ud55c',
    email: '\uc774\uba54\uc77c',
    password: '\ube44\ubc00\ubc88\ud638',
    inviteToken: '\ucd08\ub300 \ud1a0\ud070',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: '\ube44\ubc00\ubc88\ud638 \uc785\ub825',
    invitePlaceholder: '\ucd08\ub300 \ud1a0\ud070 \ubd99\uc5ec\ub123\uae30',
    pleaseWait: '\uc7a0\uc2dc\ub9cc\uc694\u2026',
    continue: '\uacc4\uc18d',
    createAccount: '\uacc4\uc815 \ub9cc\ub4e4\uae30',
    noAccount: '\uacc4\uc815\uc774 \uc5c6\uc73c\uc2e0\uac00\uc694? ',
    register: '\uac00\uc785\ud558\uae30',
    haveAccount: '\uc774\ubbf8 \uacc4\uc815\uc774 \uc788\uc73c\uc2e0\uac00\uc694? ',
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
    streak: '\uc77c \uc5f0\uc18d',
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
    signInSub: '\u767b\u5f55\u60a8\u7684\u6863\u6848\u5e93',
    registerSub: '\u5185\u6d4b\u9636\u6bb5 - \u9700\u8981\u9080\u8bf7\u7801',
    limitedSpots: '\u540d\u989d\u6709\u9650',
    email: '\u90ae\u7bb1',
    password: '\u5bc6\u7801',
    inviteToken: '\u9080\u8bf7\u7801',
    emailPlaceholder: 'you@example.com',
    passwordPlaceholder: '\u8bf7\u8f93\u5165\u5bc6\u7801',
    invitePlaceholder: '\u7c98\u8d34\u60a8\u7684\u9080\u8bf7\u7801',
    pleaseWait: '\u8bf7\u7a0d\u5019\u2026',
    continue: '\u7ee7\u7eed',
    createAccount: '\u521b\u5efa\u8d26\u6237',
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
    streak: '\u5929\u8fde\u7eed',
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
