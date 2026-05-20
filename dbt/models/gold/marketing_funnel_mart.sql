with events as (
    select *
    from {{ ref('fct_web_events') }}
),

session_metrics as (
    select
        session_id,
        min(customer_id) as customer_id,
        min(utm_source) as utm_source,
        min(occurred_at) as session_started_at,
        count(*) filter (where event_name = 'page_view') as page_views,
        count(*) filter (where event_name = 'product_view') as product_views,
        count(*) filter (where event_name = 'add_to_cart') as add_to_carts,
        count(*) filter (where event_name = 'checkout_started') as checkouts,
        count(*) filter (where event_name = 'purchase') as purchases
    from events
    group by 1
)

select
    utm_source,
    count(*) as sessions,
    sum(page_views) as page_views,
    sum(product_views) as product_views,
    sum(add_to_carts) as add_to_carts,
    sum(checkouts) as checkouts,
    sum(purchases) as purchases,
    (sum(add_to_carts)::numeric / nullif(sum(product_views), 0))::numeric(12, 4) as cart_rate,
    (sum(purchases)::numeric / nullif(sum(checkouts), 0))::numeric(12, 4) as checkout_conversion_rate
from session_metrics
group by 1
