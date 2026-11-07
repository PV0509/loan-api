create table if not exists predictions (
    id               serial primary key,
    created_at       timestamptz not null default now(),
    income           numeric not null,
    loan_amount      numeric not null,
    loan_term        integer not null,
    credit_score     numeric not null,
    employment_years integer not null,
    approved         boolean not null,
    probability      numeric not null,
    model_version    text not null
);
