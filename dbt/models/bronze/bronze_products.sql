select
    product_id,
    trim(product_name) as product_name,
    lower(trim(category)) as category,
    unit_price::numeric(12, 2) as unit_price,
    updated_at,
    ingested_at
from {{ source('raw', 'raw_products') }}
