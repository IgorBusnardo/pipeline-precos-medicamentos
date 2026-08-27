{{ config(materialized='view') }}

-- Grao: apresentacao (GGREM) x competencia.
-- Atributos cadastrais e os precos "sem impostos", que nao pertencem a nenhuma
-- faixa de ICMS e por isso ficam fora do fato de preco por aliquota.

with fonte as (

    select * from {{ source('raw', 'cmed_precos') }}

),

limpo as (

    select
        -- GGREM sozinho NAO e unico: a CMED reaproveitou o codigo
        -- 541821110172303 em dois medicamentos distintos na competencia de
        -- 2025-07. A chave estavel e GGREM + registro ANVISA.
        md5(trim(ggrem) || '|' || trim(registro)) as sk_produto,
        trim(ggrem)                                as ggrem,
        cast(snapshot_date as date)                as snapshot_date,

        trim(substancia)                           as substancia,
        trim(cnpj)                                 as cnpj,
        trim(laboratorio)                          as laboratorio,
        trim(produto)                              as produto,
        trim(apresentacao)                         as apresentacao,
        trim(registro)                             as registro,
        nullif(trim(ean_1), '-')                   as ean_1,

        trim(classe_terapeutica)                   as classe_terapeutica_raw,
        -- 'D5X - OUTROS PRODUTOS ...' -> codigo + descricao
        case
            when classe_terapeutica like '%-%'
            then trim(split_part(classe_terapeutica, '-', 1))
        end                                        as classe_codigo,
        case
            when classe_terapeutica like '%-%'
            then trim(substr(classe_terapeutica, position('-' in classe_terapeutica) + 1))
            else trim(classe_terapeutica)
        end                                        as classe_descricao,

        trim(tipo_produto)                         as tipo_produto,
        trim(regime_preco)                         as regime_preco,
        trim(lista_pis_cofins)                     as lista_pis_cofins,
        trim(tarja)                                as tarja,
        trim(destinacao_comercial)                 as destinacao_comercial,

        {{ sim_nao_to_bool('restricao_hospitalar') }} as flag_restricao_hospitalar,
        {{ sim_nao_to_bool('cap') }}                  as flag_cap,
        {{ sim_nao_to_bool('confaz_87') }}            as flag_confaz_87,
        {{ sim_nao_to_bool('icms_zero') }}            as flag_icms_zero,
        {{ sim_nao_to_bool('comercializacao_ano_anterior') }} as flag_comercializado_ano_anterior,
        cast(ano_comercializacao as integer)       as ano_comercializacao,

        {{ brl_to_decimal('pf_sem_impostos') }}    as pf_sem_impostos,
        {{ brl_to_decimal('pmc_sem_impostos') }}   as pmc_sem_impostos,

        arquivo_origem,
        ingerido_em

    from fonte

)

select * from limpo
