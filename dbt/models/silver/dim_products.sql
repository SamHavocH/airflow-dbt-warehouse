select
    product_id,
    product_name,
    category,
    unit_price,
    updated_at
from {{ ref('bronze_products') }}
