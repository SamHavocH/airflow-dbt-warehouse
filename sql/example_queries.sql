-- Customer segments for a stakeholder-ready revenue view.
select
    customer_segment,
    count(*) as customers,
    sum(lifetime_revenue) as segment_revenue
from gold.customer_revenue_mart
group by 1
order by segment_revenue desc;

-- Daily revenue trend with a moving average.
select
    date_day,
    completed_orders,
    gross_revenue,
    revenue_7d_avg
from gold.daily_revenue_mart
order by date_day desc
limit 14;

-- Marketing funnel performance by acquisition source.
select
    utm_source,
    sessions,
    product_views,
    add_to_carts,
    purchases,
    cart_rate,
    checkout_conversion_rate
from gold.marketing_funnel_mart
order by purchases desc;
