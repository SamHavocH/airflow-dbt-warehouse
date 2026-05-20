with recursive date_spine as (
    select date '2026-04-01' as date_day

    union all

    select (date_day + interval '1 day')::date
    from date_spine
    where date_day < date '2026-12-31'
)

select
    date_day,
    extract(isodow from date_day)::int as day_of_week,
    extract(day from date_day)::int as day_of_month,
    extract(week from date_day)::int as week_of_year,
    extract(month from date_day)::int as month_number,
    extract(quarter from date_day)::int as quarter_number,
    extract(year from date_day)::int as year_number,
    case when extract(isodow from date_day)::int in (6, 7) then true else false end as is_weekend
from date_spine
