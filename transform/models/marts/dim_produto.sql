-- Grao: apresentacao (sk_produto = GGREM + registro), com os atributos da competencia mais recente em
-- que ela apareceu. `primeira_competencia` / `ultima_competencia` respondem
-- entrada e saida de portfolio sem precisar de SCD tipo 2.

with base as (

    select
        *,
        row_number() over (partition by sk_produto order by snapshot_date desc) as rn,
        min(snapshot_date) over (partition by sk_produto) as primeira_competencia,
        max(snapshot_date) over (partition by sk_produto) as ultima_competencia,
        count(*)           over (partition by sk_produto) as qtd_competencias
    from {{ ref('stg_cmed__produtos') }}

)

select
    sk_produto,
    ggrem,
    cnpj,
    classe_codigo,
    substancia,
    produto,
    apresentacao,
    registro,
    ean_1,
    tipo_produto,
    regime_preco,
    lista_pis_cofins,
    tarja,
    destinacao_comercial,
    flag_restricao_hospitalar,
    flag_cap,
    flag_confaz_87,
    flag_icms_zero,
    primeira_competencia,
    ultima_competencia,
    qtd_competencias
from base
where rn = 1
