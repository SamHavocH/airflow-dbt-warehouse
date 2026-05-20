select
    event_id,
    customer_id,
    session_id,
    lower(event_name) as event_name,
    occurred_at,
    occurred_at::date as event_date,
    lower(utm_source) as utm_source,
    loaded_at
from {{ source('raw', 'raw_events') }}
