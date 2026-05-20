with source as (
    select *
    from {{ source('raw', 'raw_customers') }}
),

ranked as (
    select
        customer_id,
        trim(full_name) as full_name,
        lower(trim(email)) as email,
        upper(country) as country_code,
        trim(city) as city,
        created_at,
        updated_at,
        ingested_at,
        row_number() over (
            partition by customer_id
            order by updated_at desc, ingested_at desc
        ) as row_number_latest
    from source
)

select *
from ranked
where row_number_latest = 1
