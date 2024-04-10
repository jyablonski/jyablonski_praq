-- order by grade desc
-- if 1 student have multiple >= 80% grades, order them by name alphabetically
-- if grade is < 80%, null the name out and list them by descending grade order

-- this problem was dumb as fuck & a waste of time.  wtf are these equality joins
select
    case when Grades.grade < 8 then null else Students.name end as name,
    Grades.grade,
    Students.marks
from Students
    inner join Grades on Students.Marks >= Grades.Min_Mark and Students.Marks <= Grades.Max_Mark
order by 
    Grades.grade desc,
    Students.name,
    Students.marks