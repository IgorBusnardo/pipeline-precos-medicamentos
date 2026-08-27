-- Variacao do Preco Fabrica entre competencias consecutivas, na faixa de ICMS
-- 18% (a mais comum). Uma linha por apresentacao por par de competencias.
--
-- Reajustes fora de [-30%, +30%] sao marcados como outlier em vez de removidos:
-- quase sempre sao rerregistro de apresentacao reusando o GGREM, nao reajuste.
-- A decisao de excluir fica com quem consome, nao escondida no pipeline.

with precos as (

    select sk_produto, ggrem, snapshot_date, pf
    from {{ ref('fct_preco') }}
    where aliquota_icms = 18
      and area_livre_comercio = false
      and pf > 0

),

par as (

    select
        sk_produto,
        ggrem,
        lag(snapshot_date) over (partition by sk_produto order by snapshot_date) as competencia_anterior,
        snapshot_date                                                      as competencia_atual,
        lag(pf) over (partition by sk_produto order by snapshot_date)           as pf_anterior,
        pf                                                                 as pf_atual
    from precos

),

calculo as (

    select
        sk_produto,
        ggrem,
        competencia_anterior,
        competencia_atual,
        pf_anterior,
        pf_atual,
        round((pf_atual / pf_anterior - 1) * 100, 4) as variacao_pct
    from par
    where competencia_anterior is not null

)

select
    c.*,
    abs(c.variacao_pct) > 30                     as flag_outlier,
    d.tipo_produto,
    d.regime_preco,
    d.lista_pis_cofins,
    d.classe_codigo,
    d.cnpj
from calculo c
left join {{ ref('dim_produto') }} d using (sk_produto)
