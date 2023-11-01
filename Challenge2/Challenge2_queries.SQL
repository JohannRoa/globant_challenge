--Challenge 2 queries


---This query was just used for exploring the distribution of years in the data
with a as (
SELECT department_id,EXTRACT(YEAR FROM datetime::date) as year
FROM employees)
select department_id,year,count(*) from a group by  1,2 order by 1;

WITH a as (
SELECT job_id,EXTRACT(YEAR FROM datetime::date) as year
FROM employees)
select job_id,year,count(*) from a group by  1,2 order by 1;


---The query below determines the number of employees hired for each job and department in 2021 divided by quarter
with A AS(
select *
from (select * from employees where EXTRACT(YEAR FROM datetime::date) = 2021 ) e
join departments d on d.id = e.department_id
join jobs j on e.job_id = j.id)
SELECT department,job,
    SUM(CASE WHEN EXTRACT(QUARTER FROM datetime::date) = 1 THEN 1 ELSE 0 END) AS q1_employee_count,
    SUM(CASE WHEN EXTRACT(QUARTER FROM datetime::date) = 2 THEN 1 ELSE 0 END) AS q2_employee_count,
    SUM(CASE WHEN EXTRACT(QUARTER FROM datetime::date) = 3 THEN 1 ELSE 0 END) AS q3_employee_count,
    SUM(CASE WHEN EXTRACT(QUARTER FROM datetime::date) = 4 THEN 1 ELSE 0 END) AS q4_employee_count
FROM A
group by department,job
order by department asc, job asc;



--- This query give us List of ids, name and number of employees hired of each department that hired more
---     employees than the mean of employees hired in 2021 for all the departments
WITH EmployeesByDepartment2021 AS (
    SELECT
        d.id AS department_id,
        COUNT(*) AS department_employee_count
    FROM (select * from employees where EXTRACT(YEAR FROM datetime::date) = 2021 ) e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.id
),
MeanEmployeeCount AS (
    SELECT AVG(department_employee_count) AS mean_employee_count
    FROM EmployeesByDepartment2021
),
EmployeesByDepartment AS (SELECT
        d.id AS department_id,
        d.department,
        COUNT(*) AS department_employee_count
    FROM (select * from employees where EXTRACT(YEAR FROM datetime::date) = 2021 ) e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.id, d.department),
EmployeesGreaterThan2021 AS (
SELECT department_id, department, department_employee_count
from EmployeesByDepartment ebd
    cross join MeanEmployeeCount mec
where department_employee_count> mec.mean_employee_count)
SELECT * FROM EmployeesGreaterThan2021 order by  department_employee_count desc;
