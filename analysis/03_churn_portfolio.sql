-- Pergunta: quais apresentacoes sairam e entraram na lista entre competencias?
-- Saida de generico barato e o sinal que antecede desabastecimento.
--
-- As competencias nao sao fixas na query: vem do proprio dado, para a analise
-- continuar valendo quando uma competencia nova entrar no pipeline.

with janela as (
    select min(snapshot_date) as primeira, max(snapshot_date) as ultima
    from main_marts.fct_produto_snapshot
),

movimento as (
    select
        d.sk_produto,
        d.tipo_produto,
        case
            when d.primeira_competencia = j.primeira
             and d.ultima_competencia   = j.ultima     then 'permaneceu'
            when d.ultima_competencia   < j.ultima     then 'saiu'
            when d.primeira_competencia > j.primeira   then 'entrou'
        end as movimento
    from main_marts.dim_produto d
    cross join janela j
)

select movimento, tipo_produto, count(*) as qtd
from movimento
group by 1, 2
order by 1, qtd desc;


-- Faixa de preco de quem entrou ou saiu vs quem permaneceu nas duas competencias.
select
    case when d.qtd_competencias > 1 then 'permaneceu' else 'entrou ou saiu' end as grupo,
    count(distinct d.sk_produto)   as qtd_apresentacoes,
    round(median(p.pf), 2)         as pf_mediano
from main_marts.dim_produto d
join main_marts.fct_preco p
  on p.sk_produto = d.sk_produto
 and p.aliquota_icms = 18
 and not p.area_livre_comercio
group by 1;
