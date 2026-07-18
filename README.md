# 🏥 RCM Revenue Benchmarking (Python + MySQL)

## 🎯 What This Project Does

This project solves a critical healthcare finance problem:

**"Why is our money taking so long to arrive?"**

Healthcare providers process 1,000+ claims per month but don't know:
- How long until insurance pays us? (AR - Accounts Receivable)
- How many claims get rejected? (Denial Rate)
- Which insurance companies are the slowest?
- Why are claims being rejected?

**Current System:** Wait until month-end → Pull Excel reports → Discover problems → Too late to fix

**Better Way (This Project):** Every day → Automated scorecard → See problems instantly → Fix before month-end

---

## 🏢 The Business Problem

### The Situation

A hospital group processes 1,093 claims over 2 years:
- 942 get paid (approved)
- 137 get denied (rejected)
- Average payment time: 44 days

**But here's the problem:**
- Commercial insurance pays in 35 days ✅
- Medicare pays in 51 days ⚠️
- Medicaid pays in 57 days ❌
- Self-pay takes 64 days ❌

**Cost:** Every day a claim sits unpaid = cash flow problem = operational stress

**Denial Problem:** 12.5% of claims get rejected
- Some are preventable (missing info, coding errors)
- Some are specific to each payer

**Current Reality:**
- No visibility into problems until month-end
- Can't prioritize which claims to follow up on
- No data on which payers cause most delays

### What This Project Solves

This tool asks 5 critical questions EVERY DAY:

```
Question 1: How long until we get paid?
Target: < 40 days
Your Result: 44 days ⚠️

Question 2: How many claims get rejected?
Target: < 10%
Your Result: 12.5% ⚠️

Question 3: How many are approved first try?
Target: > 90%
Your Result: 69.8% ❌

Question 4: Are we collecting what we should?
Target: > 95%
Your Result: 95.1% ✅

Question 5: How long before we submit claims?
Target: < 5 days
Your Result: 5.4 days ⚠️
```

Then it breaks it down by insurance company:

```
Commercial: 35 days, 9.8% deny ✅ BEST
Medicare: 51 days, 13.6% deny ⚠️
Medicaid: 57 days, 15.8% deny ❌
Self-Pay: 64 days, 18.5% deny ❌ WORST
```

**The Insight:** Medicaid and Self-Pay are the problem, NOT Commercial insurance.

---

## 📊 The Data

| Table | Records | What It Contains |
|-------|---------|-----------------|
| providers | 15 | Doctors/clinics submitting claims |
| payers | 7 | Insurance companies (Commercial, Medicare, Medicaid, Self-Pay) |
| claims | 1,093 | Individual medical claims |
| payments | 942 | Payments received from insurance |
| denials | 137 | Rejected claims with reason codes |

**Example:**
```
Claim 1: Dr. Smith → Commercial Insurance → Submitted Jan 1 → Paid Jan 28 (27 days) ✅
Claim 2: Dr. Smith → Medicaid → Submitted Jan 1 → Paid Feb 28 (58 days) ❌
Claim 3: Dr. Smith → Medicaid → Denied Jan 15 (reason: Missing auth) ❌
```

---

## 🛠️ Tech Stack

- **MySQL** - Database (healthcare claims)
- **Python** - Analysis automation
  - pandas (data manipulation)
  - mysql-connector-python (database connection)
  - python-dotenv (environment variables)
- **SQL** - Queries (DATEDIFF, GROUP BY, aggregations)
- **Docker** - Easy setup (no installation)

---

## 💻 How to Set It Up

### Option 1: Docker (EASIEST - Recommended)

**You need:** Docker Desktop installed on Mac

```bash
# Step 1: Download the project
git clone https://github.com/mprantikk/rcm-revenue-benchmarking.git
cd rcm-revenue-benchmarking

# Step 2: Start the database
docker-compose up -d

# Step 3: Install Python tools
pip install -r requirements.txt

# Step 4: Setup environment
cp .env.example .env

# Done! Database is running, Python is ready.
```

### Option 2: Local MySQL (If Docker doesn't work)

```bash
# Install MySQL
brew install mysql@8.0

# Start MySQL
brew services start mysql@8.0

# Create database
mysql -u root -p -e "CREATE DATABASE rcm_benchmarking;"

# Load schema and data
mysql -u root -p rcm_benchmarking < schema.sql
mysql -u root -p rcm_benchmarking < seed_data.sql

# Install Python tools
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

---

## 🏃 How to Run the Analysis

```bash
# Run the complete benchmarking analysis
python rcm_benchmarking.py
```

**You'll see output like:**

```
Computing RCM benchmark KPIs...

=== RCM Benchmark Scorecard ===
metric                  value      target    status
avg_days_in_ar          44.4 days  < 40      ⚠️ Above target
denial_rate_pct         12.5%      < 10%     ⚠️ Above target
clean_claim_rate_pct    69.8%      > 90%     ⚠️ Below target
net_collection_rate_pct 95.1%      > 95%     ✅ On target
avg_charge_lag_days     5.4 days   < 5       ⚠️ Slightly above

=== Denial Rate by Payer Type ===
payer_type    denial_rate_pct  total_claims
Self-Pay      18.5%            108
Medicaid      15.8%            189
Medicare      13.6%            196
Commercial    9.8%             600

=== Top 5 Denial Reasons ===
code    reason                               occurrences  impact
PR-1    Deductible amount                    27           $30,700
CO-97   Benefit included in another service  26           $30,000
CO-16   Claim lacks information              24           $28,500
CO-11   Diagnosis inconsistent with procedure 24         $31,500
CO-50   Non-covered service                  18           $14,900

Saved: kpi_scorecard.csv, monthly_revenue_trend.csv
```

---

## 📈 Key Findings

### The Numbers

| Metric | Result | Industry Target |
|--------|--------|-----------------|
| Total Claims | 1,093 | - |
| Approved Claims | 942 (86.2%) | - |
| Denied Claims | 137 (12.5%) | < 10% |
| Days in AR | 44 days | < 40 days |
| Denial Rate | 12.5% | < 10% |
| Clean Claim Rate | 69.8% | > 90% |
| Net Collection Rate | 95.1% | > 95% |
| Charge Lag | 5.4 days | < 5 days |

### The Real Discovery

**Payer Mix Matters More Than Provider Quality**

```
Insurance Type    Days to Pay    Denial Rate    Problem Level
Commercial        35 days        9.8%           ✅ GOOD
Medicare          51 days        13.6%          ⚠️ MEDIUM  
Medicaid          57 days        15.8%          ❌ BAD
Self-Pay          64 days        18.5%          ❌ VERY BAD
```

**What This Means:**
- Self-Pay takes 83% LONGER than Commercial
- Medicaid denies at 60% HIGHER rate than Commercial
- Not a provider performance issue
- **It's a front-end/eligibility verification issue**

### Why It Matters

**Current Loss:** $40,000+ per year in preventable delays and denials

**What We Can Fix:**
1. **Missing Information (CO-16):** 24 claims, $28,500 → Fix with better claim scrubbing
2. **Coding Errors (CO-11):** 24 claims, $31,500 → Fix with better documentation review
3. **Medicaid Delays:** 57-day AR → Fix with pre-authorization verification

**Opportunity:** Implementing these fixes could recover $40,000+ annually

---

## 💡 Business Actions

### Immediate (Next 30 Days)

1. **Implement claim scrubbing before submission**
   - Check for missing fields
   - Validate diagnosis codes
   - Reduce CO-16 and CO-11 denials by 50%
   - Estimated recovery: $30,000 per year

2. **Create Medicaid pre-auth process**
   - Verify coverage before submitting claims
   - Reduce Medicaid AR from 57 to 50 days
   - Estimated cash flow improvement: $25,000+

3. **Setup daily monitoring**
   - Run this script daily
   - Alert when denial rate exceeds 14%
   - Alert when AR exceeds 45 days

### Medium-Term (Next 90 Days)

1. **Payer-specific workflows**
   - Commercial: Fast track (35 days is good)
   - Medicare: Standard with follow-up at day 40
   - Medicaid: Manual verification pre-submission
   - Self-Pay: Require payment plan agreement upfront

2. **Provider coaching**
   - Identify providers with above-average denial rates
   - Focus training on documentation
   - Track individual clean claim rates

### Long-Term (Strategic)

1. **Automation:** Automate daily KPI calculation and reporting
2. **Prediction:** Use machine learning to identify high-risk claims before submission
3. **Optimization:** Appeal prioritization (high-dollar denials first)
4. **Compliance:** Audit trail for all claim status changes

---

## 📁 Folder Structure

```
rcm-revenue-benchmarking/
├── README.md                    ← You're reading this
├── docker-compose.yml           ← Spin up database
├── .gitignore                   ← GitHub ignore file
├── .env.example                 ← Environment settings template
├── LICENSE                      ← MIT License
├── requirements.txt             ← Python packages needed
├── schema.sql                   ← Database structure
├── seed_data.sql                ← Sample healthcare data
├── benchmarking_queries.sql     ← SQL queries (reference)
├── rcm_benchmarking.py          ← Main Python script
└── insights.md                  ← Detailed analysis findings
```

---

## 🔍 Understanding the Code

### rcm_benchmarking.py

The main Python script does 5 things:

1. **Connect to MySQL**
   - Uses credentials from `.env` file
   - Tests connection with error handling

2. **Calculate KPIs**
   - Days in AR: DATEDIFF(payment_date, service_date)
   - Denial Rate: COUNT claims where status='denied' / total claims
   - Clean Claim Rate: Claims paid with 0 resubmissions
   - Collection Rate: SUM(paid) / SUM(allowed)
   - Charge Lag: DATEDIFF(submission_date, service_date)

3. **Compare to Benchmarks**
   - Industry targets loaded at top of script
   - Marks each KPI as ✅ On Target or ⚠️ Above/Below Target

4. **Segment by Payer Type**
   - Groups all claims by: Commercial, Medicare, Medicaid, Self-Pay
   - Calculates metrics per payer
   - Identifies problem payers

5. **Export Results**
   - Saves to CSV for further analysis
   - Prints scorecard to console
   - Ready for email/dashboard integration

---

## 📊 SQL Concepts Used

- **DATEDIFF:** Calculate days between two dates
- **GROUP BY:** Group claims by payer, provider, date
- **COUNT FILTER:** Count with conditions (claims that are denied, etc.)
- **SUM:** Total amounts (total allowed, total collected)
- **RANK WINDOW FUNCTION:** Rank providers by performance
- **LEFT JOIN:** Keep all claims even if no payment/denial record

---

## 📖 For Hiring Managers

This project demonstrates:

**Python Skills:**
- Database connection and error handling
- Data processing with pandas
- Environment variable management
- CSV export and reporting
- Clean code structure with functions

**SQL Skills:**
- Database schema design (normalized)
- Complex queries with calculations
- Date arithmetic (critical for healthcare)
- Conditional aggregation
- Performance optimization with indexes

**Healthcare Domain Knowledge:**
- Understanding of RCM (Revenue Cycle Management)
- Awareness of denial reasons and payer behavior
- Recognition of operational challenges
- Actionable business recommendations

**Analytics Thinking:**
- Identifying root causes (payer mix, not provider quality)
- Quantifying financial impact ($40K+ opportunity)
- Recommending specific, measurable actions
- Building dashboards for stakeholder reporting

---

## 🚀 How to Extend This

1. **Real Healthcare Data:** Connect to actual hospital claims system (Epic EHR, Cerner, etc.)
2. **Airflow Orchestration:** Schedule daily runs with alerts
3. **Power BI Dashboard:** Real-time scorecard with drill-downs
4. **Machine Learning:** Predict which claims will be denied before submission
5. **Appeals Management:** Prioritize high-impact denials for follow-up
6. **Compliance Audit:** Track all claim status changes and maintain audit trail

---

## 📄 License

MIT License - Anyone can use, modify, and distribute this code.

---

## 📝 Resume Bullet Point

> Built a Python + MySQL RCM benchmarking tool computing 5 healthcare KPIs (Days in AR, denial rate, clean claim rate, net collection rate, charge lag) across 1,093 synthetic claims, isolating that self-pay and Medicaid payers drive 50% higher denial rates and 83% longer payment cycles due to front-end eligibility gaps — enabling $40K+ annual recovery opportunity through pre-submission verification.

---

## 📧 Get In Touch

Have questions about the analysis or healthcare RCM strategies?

Connect on LinkedIn: https://linkedin.com/in/mprantikk

---

## 🏥 What Hospitals Learn From This

This tool teaches hospitals HOW to think about cash flow:
- Not all insurance companies are equal
- Some payers require different workflows
- Prevention (proper submission) beats cure (appealing denials)
- Data-driven decisions beat guessing
- Daily monitoring beats monthly surprises
