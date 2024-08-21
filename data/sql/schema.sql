CREATE DATABASE apptracker;

\c apptracker;

CREATE TABLE resume (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

CREATE TABLE posting (
    id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    salary DOUBLE PRECISION,
    description TEXT,
    responsibilities VARCHAR NOT NULL,
    qualifications VARCHAR NOT NULL,
    remote BOOLEAN
);

CREATE TABLE application (
    id SERIAL PRIMARY KEY,
    posting_id INT NOT NULL REFERENCES posting(id),
    resume_id INT NOT NULL REFERENCES resume(id),
    date_submitted DATE NOT NULL
);

CREATE TABLE response_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE TABLE response (
    id SERIAL PRIMARY KEY,
    application_id INT NOT NULL REFERENCES application(id),
    response_type_id INT NOT NULL REFERENCES response_type(id),
    date_received DATE NOT NULL,
    data TEXT
);

INSERT INTO response_type (name)
VALUES
    ('email'),
    ('call'),
    ('sms'),
    ('interview'),
    ('takehome');

CREATE INDEX idx_application_posting_id ON application(posting_id);
CREATE INDEX idx_application_resume_id ON application(resume_id);
CREATE INDEX idx_responses_application_id ON response(application_id);
CREATE INDEX idx_responses_response_type_id ON response(response_type_id);
