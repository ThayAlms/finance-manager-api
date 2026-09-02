CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
    user_id UUID NOT NULL REFERENCES users(id),
    CONSTRAINT uk_category_name_type_user UNIQUE (name, type, user_id)
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    type VARCHAR(30) NOT NULL CHECK (type IN ('CHECKING', 'SAVINGS', 'WALLET', 'INVESTMENT')),
    balance NUMERIC(19, 2) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    CONSTRAINT uk_account_name_user UNIQUE (name, user_id)
);

CREATE TABLE financial_transactions (
    id UUID PRIMARY KEY,
    description VARCHAR(160) NOT NULL,
    amount NUMERIC(19, 2) NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'COMPLETED', 'CANCELLED')),
    category_id UUID NOT NULL REFERENCES categories(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE goals (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    target_amount NUMERIC(19, 2) NOT NULL CHECK (target_amount > 0),
    current_amount NUMERIC(19, 2) NOT NULL CHECK (current_amount >= 0),
    deadline DATE,
    user_id UUID NOT NULL REFERENCES users(id)
);

CREATE INDEX idx_transactions_user_date ON financial_transactions(user_id, transaction_date);
CREATE INDEX idx_transactions_category ON financial_transactions(category_id);
CREATE INDEX idx_goals_user ON goals(user_id);
