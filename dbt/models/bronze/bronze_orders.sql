with source as (
    select *
    from {{ source('raw', 'raw_orders') }}
),

ranked as (
    select
        order_id,
        customer_id,
        product_id,
        ordered_at,
        ordered_at::date as order_date,
        quantity,
        unit_price::numeric(12, 2) as unit_price,
        discount_amount::numeric(12, 2) as discount_amount,
        status,
        updated_at,
        ingested_at,
        row_number() over (
            partition by order_id
            order by updated_at desc, ingested_at desc
        ) as row_number_latest
    from source
)

select *
from ranked
where row_number_latest = 1
