select
    event_id,
    customer_id,
    session_id,
    event_name,
    event_date,
    occurred_at,
    utm_source,
    loaded_at,
    row_number() over (
        partition by session_id
        order by occurred_at
    ) as event_sequence_in_session
from {{ ref('bronze_events') }}
