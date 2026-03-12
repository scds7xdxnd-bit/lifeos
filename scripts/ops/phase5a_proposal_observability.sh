#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"

WINDOW_HOURS="${WINDOW_HOURS:-24}"

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<SQL
\\pset footer off
\\pset format aligned
\\pset border 2
\\echo 'Phase 5a proposal observability snapshot'
\\echo '---------------------------------------'
SELECT
  COUNT(*) AS proposals_total,
  SUM(CASE WHEN status = 'proposed' THEN 1 ELSE 0 END) AS proposals_pending,
  SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS proposals_accepted,
  SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS proposals_rejected
FROM interpretation;

\\echo ''
\\echo 'Feedback totals (last' :WINDOW_HOURS 'hours)'
SELECT
  feedback_type,
  COUNT(*) AS count
FROM user_feedback_event
WHERE created_at >= NOW() - INTERVAL '${WINDOW_HOURS} hours'
GROUP BY feedback_type
ORDER BY feedback_type;

\\echo ''
\\echo 'Feedback rates (last' :WINDOW_HOURS 'hours)'
SELECT
  ROUND(
    100.0 * SUM(CASE WHEN feedback_type = 'accepted' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0),
    2
  ) AS accept_rate_pct,
  ROUND(
    100.0 * SUM(CASE WHEN feedback_type = 'rejected' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0),
    2
  ) AS reject_rate_pct,
  ROUND(
    100.0 * SUM(CASE WHEN feedback_type = 'corrected' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0),
    2
  ) AS correct_rate_pct
FROM user_feedback_event
WHERE created_at >= NOW() - INTERVAL '${WINDOW_HOURS} hours';
SQL
