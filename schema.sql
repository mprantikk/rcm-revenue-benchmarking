-- ============================================================
-- RCM Revenue Benchmarking (Python + MySQL)
-- Schema: schema.sql
-- Written for MySQL 8.0+
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS denials;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS payers;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE providers (
    provider_id     INT AUTO_INCREMENT PRIMARY KEY,
    provider_name   VARCHAR(120) NOT NULL,
    specialty       VARCHAR(80) NOT NULL,
    location        VARCHAR(80) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE payers (
    payer_id        INT AUTO_INCREMENT PRIMARY KEY,
    payer_name      VARCHAR(120) NOT NULL,
    payer_type      ENUM('Commercial','Medicare','Medicaid','Self-Pay') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE claims (
    claim_id            INT AUTO_INCREMENT PRIMARY KEY,
    provider_id         INT NOT NULL,
    payer_id            INT NOT NULL,
    service_date        DATE NOT NULL,
    submission_date     DATE NOT NULL,
    billed_amount        DECIMAL(10,2) NOT NULL CHECK (billed_amount >= 0),
    allowed_amount        DECIMAL(10,2),
    claim_status         ENUM('paid','denied','pending') NOT NULL,
    resubmission_count   INT NOT NULL DEFAULT 0,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    FOREIGN KEY (payer_id) REFERENCES payers(payer_id)
) ENGINE=InnoDB;

CREATE TABLE payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    claim_id        INT NOT NULL,
    payment_date    DATE NOT NULL,
    paid_amount     DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
) ENGINE=InnoDB;

CREATE TABLE denials (
    denial_id       INT AUTO_INCREMENT PRIMARY KEY,
    claim_id        INT NOT NULL,
    denial_date     DATE NOT NULL,
    denial_code     VARCHAR(10) NOT NULL,
    denial_reason   VARCHAR(150) NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
) ENGINE=InnoDB;

-- Indexes to support benchmarking queries
CREATE INDEX idx_claims_provider ON claims(provider_id);
CREATE INDEX idx_claims_payer ON claims(payer_id);
CREATE INDEX idx_claims_service_date ON claims(service_date);
CREATE INDEX idx_payments_claim ON payments(claim_id);
CREATE INDEX idx_denials_claim ON denials(claim_id);
