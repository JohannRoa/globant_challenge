CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    department VARCHAR(255)
);

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    job VARCHAR(255)
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    datetime TIMESTAMP,
    department_id INTEGER, --REFERENCES departments(id),
    job_id INTEGER --REFERENCES jobs(id)
);