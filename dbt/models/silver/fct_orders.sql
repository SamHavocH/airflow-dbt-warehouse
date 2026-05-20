{{ config(materialized='incremental', unique_key='order_id') }}

with orders as (
    select *
    from {{ ref('bronze_orders') }}
    {% if is_incremental() %}
        where updated_at >= (select coalesce(max(updated_at), '1900-01-01') from {{ this }})
    {% endif %}
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.product_id,
        o.order_date,
        o.ordered_at,
        o.quantity,
        o.unit_price,
        o.discount_amount,
        greatest((o.quantity * o.unit_price) - o.discount_amount, 0)::numeric(12, 2) as gross_revenue,
        case when o.status = 'completed' then true else false end as is_completed,
        case when o.status = 'refunded' then true else false end as is_refunded,
        o.status,
        o.updated_at
    from orders as o
)

select *
from final
