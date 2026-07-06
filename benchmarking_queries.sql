-- ============================================================
-- RCM Revenue Benchmarking
-- Analysis Queries: benchmarking_queries.sql
-- Written for MySQL 8.0+ syntax
-- ============================================================

-- ------------------------------------------------
-- 1. Days in Accounts Receivable (Days in AR)
--    Industry benchmark target: < 40 days (varies by specialty)
-- ------------------------------------------------
SELECT
    ROUND(AVG(DATEDIFF(p.payment_date, c.service_date)), 1) AS avg_days_in_ar
FROM claims c
JOIN payments p ON p.claim_id = c.claim_id
WHERE c.claim_status = 'paid';


-- ------------------------------------------------
-- 2. Days in AR by Payer Type
-- ------------------------------------------------
SELECT
    pay.payer_type,
    COUNT(DISTINCT c.claim_id)                                   AS paid_claims,
    ROUND(AVG(DATEDIFF(p.payment_date, c.service_date)), 1)      AS avg_days_in_ar
FROM claims c
JOIN payments p ON p.claim_id = c.claim_id
JOIN payers pay ON pay.payer_id = c.payer_id
WHERE c.claim_status = 'paid'
GROUP BY pay.payer_type
ORDER BY avg_days_in_ar DESC;


-- ------------------------------------------------
-- 3. Denial Rate (overall, by payer type)
--    Industry benchmark target: < 10%
-- ------------------------------------------------
SELECT
    pay.payer_type,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS denial_rate_pct,
    COUNT(*) AS total_claims
FROM claims c
JOIN payers pay ON pay.payer_id = c.payer_id
GROUP BY pay.payer_type
ORDER BY denial_rate_pct DESC;


-- ------------------------------------------------
-- 4. Top Denial Reasons
-- ------------------------------------------------
SELECT
    d.denial_code,
    d.denial_reason,
    COUNT(*)                           AS occurrences,
    ROUND(SUM(c.billed_amount), 2)     AS billed_amount_impacted
FROM denials d
JOIN claims c ON c.claim_id = d.claim_id
GROUP BY d.denial_code, d.denial_reason
ORDER BY occurrences DESC
LIMIT 10;


-- ------------------------------------------------
-- 5. Clean Claim Rate
--    (% of claims paid with zero resubmissions)
--    Industry benchmark target: > 90%
-- ------------------------------------------------
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'paid' AND resubmission_count = 0 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
    , 1) AS clean_claim_rate_pct
FROM claims;


-- ------------------------------------------------
-- 6. Net Collection Rate
--    (total collected / total allowed) — core RCM financial health metric
--    Industry benchmark target: > 95%
-- ------------------------------------------------
SELECT
    ROUND(SUM(p.paid_amount), 2)                                                 AS total_collected,
    ROUND(SUM(c.allowed_amount), 2)                                              AS total_allowed,
    ROUND(100.0 * SUM(p.paid_amount) / NULLIF(SUM(c.allowed_amount), 0), 1)      AS net_collection_rate_pct
FROM claims c
JOIN payments p ON p.claim_id = c.claim_id
WHERE c.claim_status = 'paid';


-- ------------------------------------------------
-- 7. Charge Lag (days from service to submission)
--    Industry benchmark target: < 5 days
-- ------------------------------------------------
SELECT
    ROUND(AVG(DATEDIFF(submission_date, service_date)), 1) AS avg_charge_lag_days
FROM claims;


-- ------------------------------------------------
-- 8. Monthly Revenue Benchmarking (billed vs collected)
-- ------------------------------------------------
SELECT
    DATE_FORMAT(c.service_date, '%Y-%m-01')    AS month,
    ROUND(SUM(c.billed_amount), 2)             AS billed,
    ROUND(SUM(p.paid_amount), 2)               AS collected,
    ROUND(100.0 * SUM(p.paid_amount) / NULLIF(SUM(c.billed_amount), 0), 1) AS collection_rate_pct
FROM claims c
LEFT JOIN payments p ON p.claim_id = c.claim_id
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------
-- 9. Provider-Level Benchmarking
--    Ranks providers by net collections to flag outliers
-- ------------------------------------------------
SELECT
    pr.provider_name,
    pr.specialty,
    COUNT(DISTINCT c.claim_id)                                                          AS total_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status='denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS denial_rate_pct,
    ROUND(SUM(p.paid_amount), 2)                                                        AS total_collected,
    RANK() OVER (ORDER BY SUM(p.paid_amount) DESC)                                      AS collections_rank
FROM claims c
JOIN providers pr ON pr.provider_id = c.provider_id
LEFT JOIN payments p ON p.claim_id = c.claim_id
GROUP BY pr.provider_name, pr.specialty
ORDER BY total_collected DESC;
