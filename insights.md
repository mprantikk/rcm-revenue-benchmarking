# 📈 Insights Summary

Findings from running `rcm_benchmarking.py` against the seeded dataset (15 providers, 7 payers,
1,093 claims, 942 payments, 137 denials — Jan 2023 to Dec 2024).

## Benchmark Scorecard

| KPI                     | Result   | Target   | Status          |
|--------------------------|----------|----------|------------------|
| Avg. Days in AR            | 44.4 days | < 40 days | ⚠️ Above target   |
| Denial Rate                  | 12.5%    | < 10%    | ⚠️ Above target   |
| Clean Claim Rate               | 69.8%    | > 90%    | ⚠️ Below target   |
| Net Collection Rate               | 95.1%    | > 95%    | ✅ On target       |
| Avg. Charge Lag                     | 5.4 days | < 5 days | ⚠️ Slightly above |

## 1. Days in AR by Payer Type
Self-Pay and government payers take meaningfully longer to collect than commercial plans:

| Payer Type  | Avg. Days in AR |
|-------------|-----------------|
| Self-Pay    | 64.2            |
| Medicaid    | 56.8            |
| Medicare    | 51.4            |
| Commercial  | 35.1            |

Commercial payers are the only group inside the 40-day target — Medicare, Medicaid, and Self-Pay
all run well past it, which is the single biggest driver of the overall 44.4-day average.

## 2. Denial Rate by Payer Type
Denial rate follows the same pattern:

| Payer Type  | Denial Rate |
|-------------|-------------|
| Self-Pay    | 18.5%       |
| Medicaid    | 15.8%       |
| Medicare    | 13.6%       |
| Commercial  | 9.8%        |

Commercial is the only segment under the 10% target.

## 3. Top Denial Reasons
The top five denial codes are fairly evenly spread rather than dominated by one issue:

1. **PR-1** — Deductible amount (27 occurrences, ~$30.7K billed impact)
2. **CO-97** — Benefit included in another service already adjudicated (26 occurrences, ~$30K)
3. **CO-16** — Claim lacks information needed for adjudication (24 occurrences, ~$28.5K)
4. **CO-11** — Diagnosis inconsistent with procedure (24 occurrences, ~$31.5K)
5. **CO-50** — Non-covered service, not medically necessary (18 occurrences, ~$14.9K)

CO-16 (missing information) and CO-11 (coding mismatch) are both front-end/coding issues that
are typically preventable with better claim scrubbing before submission.

## 4. Revenue Overview
- **Total billed:** ~$1.26M
- **Total collected:** ~$772K (overall collected/billed ratio: 61.3% — note this is lower than
  the Net Collection Rate above because it includes denied/pending claims with $0 collected,
  while Net Collection Rate is calculated only on paid claims against their allowed amount)
- **Net Collection Rate (paid claims only): 95.1%** — meaning once a claim is actually paid,
  Commure-style operations are collecting nearly the full allowed amount

## 5. Provider Variation
Collections varied meaningfully across providers — the top provider collected roughly 3x more
than the lowest, even accounting for claim volume differences, suggesting some providers may
benefit from coding or documentation support to close the gap.

## Takeaway

The clearest signal in this dataset: **payer mix is doing most of the damage to AR days and
denial rate.** Commercial payers are already hitting or beating every target; Medicare, Medicaid,
and especially Self-Pay are dragging the averages down. In a real RCM operation, this points to
two concrete levers: (1) tighter front-end eligibility and documentation checks for
Self-Pay/Medicaid claims before submission, and (2) a dedicated aging-AR follow-up queue
prioritized by payer type rather than treating all claims the same.
