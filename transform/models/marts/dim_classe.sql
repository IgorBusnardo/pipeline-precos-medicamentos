-- Grao: classe terapeutica (codigo ATC-like da CMED, ex.: 'C9C').
-- A classe e a unidade em que a CMED avalia concentracao de mercado, entao ela
-- vira dimensao propria e nao um atributo solto do produto.

select
    classe_codigo,
    max(classe_descricao)                    as classe_descricao,
    -- Primeiro nivel do codigo ('C9C' -> 'C'): grupo anatomico.
    left(classe_codigo, 1)                   as grupo_codigo,
    count(distinct ggrem)                    as qtd_apresentacoes,
    count(distinct cnpj)                     as qtd_laboratorios
from {{ ref('stg_cmed__produtos') }}
where classe_codigo is not null
group by 1, 3
