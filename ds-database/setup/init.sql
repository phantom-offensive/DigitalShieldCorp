-- Digital Shield Corporation Database

CREATE DATABASE shieldcorp;
\c shieldcorp

-- Create users
CREATE USER monitor_ro WITH PASSWORD 'M0n_R34d!';
CREATE USER app_user WITH PASSWORD 'Vault_Adm1n!' SUPERUSER;

-- Employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    department VARCHAR(50),
    salary INTEGER
);

INSERT INTO employees VALUES
(1, 'j.reynolds', 'James Reynolds', 'j.reynolds@digitalshield.local', 'Security', 125000),
(2, 'm.chen', 'Michelle Chen', 'm.chen@digitalshield.local', 'DevOps', 135000),
(3, 'a.kowalski', 'Adrian Kowalski', 'a.kowalski@digitalshield.local', 'SysAdmin', 115000),
(4, 'd.okafor', 'Dayo Okafor', 'd.okafor@digitalshield.local', 'Executive', 195000);

-- Credentials table (contains vault API token)
CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    service VARCHAR(100),
    username VARCHAR(100),
    token VARCHAR(200),
    notes TEXT
);

INSERT INTO credentials VALUES
(1, 'vault_api', 'vault_service', 'dsc-vault-tk-8f3a2b9c7d1e4056', 'Bearer token for ds-vault API at 10.10.30.20:8443'),
(2, 'monitoring', 'nagios', 'Monitor2026!', 'Monitoring dashboard HTTP Basic Auth'),
(3, 'aws_staging', 'AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 'AWS staging — NOT production');

-- Secrets table (encrypted values + the key is here too — realistic mistake)
CREATE TABLE secrets (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(100),
    encrypted_value TEXT,
    encryption_method VARCHAR(50),
    notes TEXT
);

INSERT INTO secrets VALUES
(1, 'domain_admin_password', 'base64:RDBtQDFuX0FkbTFuXzIwMjYh', 'base64', 'Domain admin — D0m@1n_Adm1n_2026!'),
(2, 'encryption_key', 'aes256-master-key-ds-2026-x7k9m2', 'plaintext', 'Master encryption key — ROTATE QUARTERLY'),
(3, 'vault_ssh_private_key', 'base64:LS0tLS1CRUdJTi...TRUNCATED', 'base64', 'SSH key for vaultadmin@ds-vault'),
(4, 'flag_encrypted', 'FLAG{ds_7_database_secrets_decrypted}', 'none', 'Assessment flag — ignore in production');

-- Audit log (with decoy entry)
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_name VARCHAR(50),
    action VARCHAR(100),
    source_ip VARCHAR(50)
);

INSERT INTO audit_log VALUES
(1, '2026-03-28 08:00:00', 'admin', 'login', '10.10.40.50'),
(2, '2026-03-28 09:15:00', 'monitor_ro', 'SELECT employees', '10.10.20.30'),
(3, '2026-03-28 10:30:00', 'app_user', 'UPDATE secrets', '10.10.30.20');

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor_ro;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
