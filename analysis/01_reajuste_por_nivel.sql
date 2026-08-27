-- Pergunta: o reajuste anual da CMED e um teto unico que todo mundo aplica?
-- Resposta: nao. Os reajustes se agrupam em faixas discretas, compativeis com
-- os niveis 1/2/3 que a CMED atribui conforme a concentracao da classe.
--
-- Rodar: duckdb data/cmed.duckdb < analysis/01_reajuste_por_nivel.sql

select
    round(variacao_pct, 1)                        as reajuste_pct,
    count(*)                                      as qtd_apresentacoes,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as pct_do_total
from main_marts.mart_variacao_pf
where not flag_outlier
group by 1
having count(*) >= 200
order by qtd_apresentacoes desc;


-- Mesmo corte, por tipo de produto: generico reajusta MAIS que biologico.
select
    tipo_produto,
    count(*)                                                   as qtd,
    round(median(variacao_pct), 2)                             as mediana_pct,
    round(100.0 * avg(case when variacao_pct between 5.0 and 5.12 then 1 else 0 end), 1)
                                                               as pct_no_teto
from main_marts.mart_variacao_pf
where not flag_outlier
group by 1
order by mediana_pct desc;


-- Classes terapeuticas nos extremos (so as com massa critica).
select
    v.classe_codigo,
    c.classe_descricao,
    count(*)                       as qtd,
    round(median(v.variacao_pct), 2) as mediana_pct
from main_marts.mart_variacao_pf v
join main_marts.dim_classe c using (classe_codigo)
where not v.flag_outlier
group by 1, 2
having count(*) >= 100
order by mediana_pct
limit 10;
