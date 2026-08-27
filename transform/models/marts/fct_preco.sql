-- Grao: apresentacao x competencia x faixa de ICMS.
-- Medidas aditivas: nenhuma (preco e teto, nao valor transacionado).
-- Medidas semi-aditivas para media: pf, pmc, margem_varejo_pct.
--
-- LIMITE: PF e PMC sao TETOS regulados, nao preco praticado. Nao ha desconto de
-- distribuidora, bonificacao nem preco de PDV nesta base.

select
    p.sk_preco,
    p.sk_produto,
    p.ggrem,
    p.snapshot_date,
    p.aliquota_icms,
    p.area_livre_comercio,
    p.pf,
    p.pmc,
    -- Markup maximo permitido ao varejo. Na pratica e uma constante definida
    -- pela lista PIS/COFINS -- ver analysis/02_margem_e_constante.sql.
    round(p.pmc / nullif(p.pf, 0), 4)          as fator_pmc_pf,
    round((p.pmc / nullif(p.pf, 0) - 1) * 100, 2) as margem_varejo_pct
from {{ ref('stg_cmed__precos') }} p
where p.pf is not null
