{{ config(materialized='view') }}

-- Desnormaliza as 52 colunas de preco (PF/PMC x 26 faixas) para formato longo.
-- Grao de saida: apresentacao x competencia x faixa de ICMS.
-- A faixa vive no NOME da coluna na origem ('PF 17,5 %  ALC'); aqui ela vira
-- dado, que e o que permite filtrar e agrupar por aliquota em SQL.
--
-- 'ALC' = Area de Livre Comercio / Zona Franca de Manaus, que tem faixa propria.

{% set faixas = [
    ('0',       '0',    false),
    ('12',      '12',   false),
    ('12_alc',  '12',   true ),
    ('17',      '17',   false),
    ('17_alc',  '17',   true ),
    ('17_5',    '17.5', false),
    ('17_5_alc','17.5', true ),
    ('18',      '18',   false),
    ('18_alc',  '18',   true ),
    ('19',      '19',   false),
    ('19_alc',  '19',   true ),
    ('19_5',    '19.5', false),
    ('19_5_alc','19.5', true ),
    ('20',      '20',   false),
    ('20_alc',  '20',   true ),
    ('20_5',    '20.5', false),
    ('20_5_alc','20.5', true ),
    ('21',      '21',   false),
    ('21_alc',  '21',   true ),
    ('22',      '22',   false),
    ('22_alc',  '22',   true ),
    ('22_5',    '22.5', false),
    ('22_5_alc','22.5', true ),
    ('23',      '23',   false),
    ('23_alc',  '23',   true )
] %}

with fonte as (

    select * from {{ source('raw', 'cmed_precos') }}

),

longo as (

{% for sufixo, aliquota, alc in faixas %}
    select
        md5(trim(ggrem) || '|' || trim(registro)) as sk_produto,
        trim(ggrem)                        as ggrem,
        cast(snapshot_date as date)        as snapshot_date,
        cast({{ aliquota }} as decimal(4,1)) as aliquota_icms,
        {{ alc }}                          as area_livre_comercio,
        {{ brl_to_decimal('pf_'  ~ sufixo) }} as pf,
        {{ brl_to_decimal('pmc_' ~ sufixo) }} as pmc
    from fonte
    {% if not loop.last %}union all{% endif %}
{% endfor %}

)

select
    md5(sk_produto || '|' || snapshot_date::varchar || '|' || aliquota_icms::varchar
        || '|' || area_livre_comercio::varchar) as sk_preco,
    *
from longo
