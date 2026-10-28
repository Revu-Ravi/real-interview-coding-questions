
select * from departments
--innner join
select * from employees
inner join departments
on employees.department_id=departments.department_id
order by employee_id

--left join
select * from employees e
left join departments d
on e.department_id=d.department_id
order by employee_id

--right join
select * from employees e
right join departments d
on e.department_id=d.department_id
order by employee_id

-- full outer join
select * from employees e
full outer join departments d
on e.department_id=d.department_id
order by employee_id

-- cross join
select * from employees e 
cross join departments
order by employee_id 




ALTER TABLE employees
ALTER COLUMN department_id TYPE INT
USING department_id::INT;