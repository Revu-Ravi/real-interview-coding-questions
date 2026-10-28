-- select
SELECT * from employe
--insert
insert into employe(id,name,salary) values (4, 'balu' ,7000.00)
--update
update employe
set salary = NULL
where name ='revu'
-- delete
delete from employe
where name = 'balu'

SELECT * from employe
where salary between 3000 and 4000

select * from employe
where name ilike 'r%'

select name, salary from employe
where salary = 4000

update table employe
set = 'revu'
where salary = 4000

select * from employe
where salary is null


select * from employe
where salary is not null
and name is not null

alter table employe
add column department varchar(20)