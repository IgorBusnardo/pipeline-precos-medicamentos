-- Grao: CNPJ. Um laboratorio pode aparecer com grafias diferentes entre
-- competencias; o CNPJ e a chave estavel, o nome vem da competencia mais recente.

with base as (

    select
        cnpj,
        laboratorio,
        snapshot_date,
        row_number() over (partition by cnpj order by snapshot_date desc) as rn
    from {{ ref('stg_cmed__produtos') }}
    where cnpj is not null

)

select
    cnpj,
    laboratorio                as nome_laboratorio,
    count(*) over (partition by cnpj) as qtd_competencias
from base
where rn = 1
