import type { Lang } from '@/components/landing/translations'

export interface InquiryPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  readinessPrefix: string
  readinessLink: string
  readinessSuffix: string
  requestFailed: string
  duplicateDetected: string
  refinementComplete: string
  briefGenerated: string
  refiningBrief: string
  generatingBrief: string
  form: {
    setupTitle: string
    setupSub: string
    question: string
    questionPlaceholder: string
    primaryDomain: string
    selectDomain: string
    timeframe: string
    last7Days: string
    last30Days: string
    last90Days: string
    customRange: string
    startDate: string
    endDate: string
    asOf: string
    optional: string
    asOfHint: string
    crossDomainMode: string
    crossDomainHint: string
    approvedPairProfile: string
    domainPair: string
    selectApprovedPair: string
    pairHint: string
    addOptionalContext: string
    hideOptionalContext: string
    context: string
    notEvidence: string
    contextPlaceholder: string
    contextHint: string
    generateBrief: string
    refineBrief: string
    generating: string
    refining: string
    reset: string
    refiningSelectedInquiry: string
    alertQuestion: string
    alertPrimaryDomain: string
    alertTimeframe: string
    alertStartBeforeEnd: string
    alertSelectPair: string
  }
  history: {
    title: string
    empty: string
    view: string
    refine: string
  }
  brief: {
    title: string
    subtitle: string
    noBrief: string
  }
}

const en: InquiryPageTranslations = {
  eyebrow: 'Intelligence',
  title: 'Inquiry',
  subtitle: 'Scope a question to a domain and timeframe. Evidence-backed briefs only.',
  readinessPrefix: 'Data readiness not met.',
  readinessLink: 'Check Data Readiness',
  readinessSuffix: 'for next steps before generating a brief.',
  requestFailed: 'Request failed. Please try again.',
  duplicateDetected: 'Duplicate inquiry detected - returning existing brief.',
  refinementComplete: 'Refinement complete.',
  briefGenerated: 'Brief generated.',
  refiningBrief: 'Refining your brief...',
  generatingBrief: 'Generating your brief...',
  form: {
    setupTitle: 'Inquiry Setup',
    setupSub: 'Define scope first. Generate only when the question and domain lens are explicit.',
    question: 'Question',
    questionPlaceholder: 'What exactly am I trying to understand right now?',
    primaryDomain: 'Primary domain',
    selectDomain: 'Select domain...',
    timeframe: 'Timeframe',
    last7Days: 'Last 7 days',
    last30Days: 'Last 30 days',
    last90Days: 'Last 90 days',
    customRange: 'Custom range',
    startDate: 'Start date',
    endDate: 'End date',
    asOf: 'As of',
    optional: '(optional)',
    asOfHint: 'Locks replay to a deterministic cutoff time.',
    crossDomainMode: 'Enable explicit cross-domain mode',
    crossDomainHint: 'Cross-domain claims are generated only when selected domains are explicit and evidence-backed.',
    approvedPairProfile: 'Approved domain pair profile',
    domainPair: 'Domain pair',
    selectApprovedPair: 'Select approved pair...',
    pairHint: 'Cross-domain pair profiles activate only for approved 2-domain scopes.',
    addOptionalContext: 'Add optional context',
    hideOptionalContext: 'Hide optional context',
    context: 'Context',
    notEvidence: '(not evidence)',
    contextPlaceholder: 'Optional framing context. This is not treated as factual evidence.',
    contextHint: 'User context is displayed separately and not promoted to system evidence.',
    generateBrief: 'Generate Brief',
    refineBrief: 'Refine Brief',
    generating: 'Generating...',
    refining: 'Refining...',
    reset: 'Reset',
    refiningSelectedInquiry: 'Refining selected inquiry',
    alertQuestion: 'Enter a clear question (minimum 3 characters).',
    alertPrimaryDomain: 'Select a primary domain.',
    alertTimeframe: 'Select a valid timeframe.',
    alertStartBeforeEnd: 'Timeframe start must be before end.',
    alertSelectPair: 'Select an approved cross-domain pair profile.',
  },
  history: {
    title: 'Recent Inquiries',
    empty: 'No inquiries yet. Generate your first brief above.',
    view: 'View',
    refine: 'Refine',
  },
  brief: {
    title: 'Generated Brief',
    subtitle: 'Summary first, then evidence, then limits.',
    noBrief: 'No brief generated yet.',
  },
}

const ko: InquiryPageTranslations = {
  eyebrow: '인텔리전스',
  title: '질의',
  subtitle: '질문을 도메인과 기간으로 한정하세요. 근거 기반 브리프만 생성됩니다.',
  readinessPrefix: '데이터 준비 상태가 충족되지 않았습니다.',
  readinessLink: '데이터 준비 상태 확인',
  readinessSuffix: '에서 다음 단계를 확인한 뒤 브리프를 생성하세요.',
  requestFailed: '요청에 실패했습니다. 다시 시도해 주세요.',
  duplicateDetected: '중복 질의가 감지되어 기존 브리프를 반환합니다.',
  refinementComplete: '정제가 완료되었습니다.',
  briefGenerated: '브리프가 생성되었습니다.',
  refiningBrief: '브리프를 정제하는 중...',
  generatingBrief: '브리프를 생성하는 중...',
  form: {
    setupTitle: '질의 설정',
    setupSub: '먼저 범위를 정의하세요. 질문과 도메인 렌즈가 명확할 때만 생성하세요.',
    question: '질문',
    questionPlaceholder: '지금 내가 정확히 이해하려는 것은 무엇인가요?',
    primaryDomain: '기본 도메인',
    selectDomain: '도메인 선택...',
    timeframe: '기간',
    last7Days: '최근 7일',
    last30Days: '최근 30일',
    last90Days: '최근 90일',
    customRange: '사용자 지정 범위',
    startDate: '시작일',
    endDate: '종료일',
    asOf: '기준 시점',
    optional: '(선택)',
    asOfHint: '재생 기준을 결정론적 컷오프 시점으로 고정합니다.',
    crossDomainMode: '명시적 교차 도메인 모드 활성화',
    crossDomainHint: '선택 도메인이 명확하고 근거가 있을 때만 교차 도메인 주장을 생성합니다.',
    approvedPairProfile: '승인된 도메인 페어 프로필',
    domainPair: '도메인 페어',
    selectApprovedPair: '승인된 페어 선택...',
    pairHint: '교차 도메인 페어 프로필은 승인된 2개 도메인 범위에서만 활성화됩니다.',
    addOptionalContext: '선택 컨텍스트 추가',
    hideOptionalContext: '선택 컨텍스트 숨기기',
    context: '컨텍스트',
    notEvidence: '(근거 아님)',
    contextPlaceholder: '선택 프레이밍 컨텍스트입니다. 사실 근거로 처리되지 않습니다.',
    contextHint: '사용자 컨텍스트는 별도로 표시되며 시스템 근거로 승격되지 않습니다.',
    generateBrief: '브리프 생성',
    refineBrief: '브리프 정제',
    generating: '생성 중...',
    refining: '정제 중...',
    reset: '초기화',
    refiningSelectedInquiry: '선택한 질의 정제 중',
    alertQuestion: '명확한 질문을 입력해 주세요 (최소 3자).',
    alertPrimaryDomain: '기본 도메인을 선택해 주세요.',
    alertTimeframe: '유효한 기간을 선택해 주세요.',
    alertStartBeforeEnd: '시작일은 종료일보다 이전이어야 합니다.',
    alertSelectPair: '승인된 교차 도메인 페어 프로필을 선택해 주세요.',
  },
  history: {
    title: '최근 질의',
    empty: '아직 질의가 없습니다. 위에서 첫 브리프를 생성해 보세요.',
    view: '보기',
    refine: '정제',
  },
  brief: {
    title: '생성된 브리프',
    subtitle: '요약 먼저, 근거 다음, 한계는 마지막입니다.',
    noBrief: '아직 생성된 브리프가 없습니다.',
  },
}

const zh: InquiryPageTranslations = {
  eyebrow: '智能洞察',
  title: '问询',
  subtitle: '将问题限定在领域与时间范围内。仅生成有证据支撑的简报。',
  readinessPrefix: '数据准备度未达标。',
  readinessLink: '查看数据准备度',
  readinessSuffix: '并完成下一步后再生成简报。',
  requestFailed: '请求失败，请重试。',
  duplicateDetected: '检测到重复问询，已返回现有简报。',
  refinementComplete: '精炼完成。',
  briefGenerated: '简报已生成。',
  refiningBrief: '正在精炼简报...',
  generatingBrief: '正在生成简报...',
  form: {
    setupTitle: '问询设置',
    setupSub: '先定义范围。仅在问题与领域视角明确时生成。',
    question: '问题',
    questionPlaceholder: '我现在到底想弄清楚什么？',
    primaryDomain: '主领域',
    selectDomain: '选择领域...',
    timeframe: '时间范围',
    last7Days: '最近7天',
    last30Days: '最近30天',
    last90Days: '最近90天',
    customRange: '自定义范围',
    startDate: '开始日期',
    endDate: '结束日期',
    asOf: '截至时间',
    optional: '（可选）',
    asOfHint: '将回放锁定在确定性截止时间。',
    crossDomainMode: '启用显式跨领域模式',
    crossDomainHint: '仅当所选领域明确且有证据支撑时才生成跨领域结论。',
    approvedPairProfile: '已批准的领域配对配置',
    domainPair: '领域配对',
    selectApprovedPair: '选择已批准配对...',
    pairHint: '跨领域配对配置仅在已批准的双领域范围内启用。',
    addOptionalContext: '添加可选上下文',
    hideOptionalContext: '隐藏可选上下文',
    context: '上下文',
    notEvidence: '（非证据）',
    contextPlaceholder: '可选背景说明，不会被视为事实证据。',
    contextHint: '用户上下文会单独展示，不会提升为系统证据。',
    generateBrief: '生成简报',
    refineBrief: '精炼简报',
    generating: '生成中...',
    refining: '精炼中...',
    reset: '重置',
    refiningSelectedInquiry: '正在精炼所选问询',
    alertQuestion: '请输入明确问题（至少3个字符）。',
    alertPrimaryDomain: '请选择主领域。',
    alertTimeframe: '请选择有效时间范围。',
    alertStartBeforeEnd: '开始日期必须早于结束日期。',
    alertSelectPair: '请选择已批准的跨领域配对配置。',
  },
  history: {
    title: '最近问询',
    empty: '暂无问询，请先在上方生成第一份简报。',
    view: '查看',
    refine: '精炼',
  },
  brief: {
    title: '生成简报',
    subtitle: '先总结，再证据，最后限制。',
    noBrief: '尚未生成简报。',
  },
}

const inquiryTranslations: Record<Lang, InquiryPageTranslations> = { en, ko, zh }

export function getInquiryTranslations(lang: Lang): InquiryPageTranslations {
  return inquiryTranslations[lang] ?? inquiryTranslations.en
}
