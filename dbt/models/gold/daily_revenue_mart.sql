with daily_orders as (
    select
        order_date,
        count(*) filter (where is_completed) as completed_orders,
        count(*) filter (where is_refunded) as refunded_orders,
        sum(gross_revenue) filter (where is_completed) as gross_revenue
    from {{ ref('fct_orders') }}
    group by 1
),

calendar as (
    select date_day
    from {{ ref('dim_dates') }}
    where date_day between date '2026-04-01' and date '2026-05-20'
)

select
    c.date_day,
    coalesce(d.completed_orders, 0) as completed_orders,
    coalesce(d.refunded_orders, 0) as refunded_orders,
    coalesce(d.gross_revenue, 0)::numeric(12, 2) as gross_revenue,
    avg(coalesce(d.gross_revenue, 0)) over (
        order by c.date_day
        rows between 6 preceding and current row
    )::numeric(12, 2) as revenue_7d_avg
from calendar as c
left join daily_orders as d
    on c.date_day = d.order_date
