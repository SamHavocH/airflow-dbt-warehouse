select *
from {{ ref('fct_orders') }}
where is_completed
  and quantity <= 0
