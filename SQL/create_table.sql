create table employees (employee_id int primary key, employee_name varchar(50), salary decimal(10,2),department_id varchar(20),email varchar(50),joining_data date)

insert into employees(employee_id, employee_name, salary,department_id,email,joining_data) 
values (1, 'Ravi', 60000, 10, 'ravi@gmail.com', '2022-02-18'),
(2, 'Priya', 55000, 20, 'priya@gmail.com', '2023-05-10'),
(3, 'Kiran', 70000, 10, 'kiran@gmail.com', '2021-08-15'),
(4, 'Sneha', 45000, 30, 'sneha@gmail.com', '2024-01-20'),
(5, 'Arjun', 50000, NULL, 'arjun@gmail.com', '2023-11-05');
create table departments (department_id int primary key,department_name varchar(20), location varchar(30))

insert into departments (department_id,department_name, location )
values (10, 'IT', 'Hyderabad'),
(20, 'HR', 'Bangalore'),
(30, 'Finance', 'Chennai'),
(40, 'Marketing', 'Mumbai');
