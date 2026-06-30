with orders as (
    select
        SalesPerson.name
    from SalesPerson
    inner join Orders on SalesPerson.sales_id = Orders.sales_id
    inner join Company on Orders.com_id = Company.com_id
    where Company.name = 'RED'
)

select SalesPerson.name
from SalesPerson
left join orders on Salesperson.name = orders.name
where orders.name is null