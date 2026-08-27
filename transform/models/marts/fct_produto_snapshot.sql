-- Grao: apresentacao x competencia. Estado cadastral do produto na data,
-- separado do fato de preco porque nao depende da faixa de ICMS.

select
    sk_produto,
    ggrem,
    snapshot_date,
    cnpj,
    classe_codigo,
    tipo_produto,
    regime_preco,
    lista_pis_cofins,
    flag_cap,
    flag_restricao_hospitalar,
    flag_comercializado_ano_anterior,
    ano_comercializacao,
    pf_sem_impostos,
    pmc_sem_impostos
from {{ ref('stg_cmed__produtos') }}
