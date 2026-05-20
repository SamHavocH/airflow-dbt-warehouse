select
    c.customer_id,
    c.full_name,
    c.email,
    c.country_code,
    coalesce(r.region, 'Unknown') as region,
    c.city,
    c.created_at,
    c.updated_at
from {{ ref('bronze_customers') }} as c
left join {{ ref('country_regions') }} as r
    on c.country_code = r.country_code
