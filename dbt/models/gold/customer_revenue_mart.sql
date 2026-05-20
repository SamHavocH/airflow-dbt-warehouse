with orders as (
    select *
    from {{ ref('fct_orders') }}
    where is_completed
),

customer_orders as (
    select
        c.customer_id,
        c.full_name,
        c.country_code,
        c.region,
        count(o.order_id) as completed_orders,
        sum(o.gross_revenue) as lifetime_revenue,
        min(o.order_date) as first_order_date,
        max(o.order_date) as latest_order_date
    from {{ ref('dim_customers') }} as c
    left join orders as o
        on c.customer_id = o.customer_id
    group by 1, 2, 3, 4
),

ranked as (
    select
        *,
        dense_rank() over (order by lifetime_revenue desc nulls last) as revenue_rank,
        case
            when coalesce(lifetime_revenue, 0) >= 1000 then 'high_value'
            when coalesce(lifetime_revenue, 0) >= 300 then 'growth'
            else 'new_or_low_activity'
        end as customer_segment
    from customer_orders
)

select
    customer_id,
    full_name,
    country_code,
    region,
    completed_orders,
    coalesce(lifetime_revenue, 0)::numeric(12, 2) as lifetime_revenue,
    first_order_date,
    latest_order_date,
    revenue_rank,
    customer_segment
from ranked
