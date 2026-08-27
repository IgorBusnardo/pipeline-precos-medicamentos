-- Pergunta: a margem que a regulacao permite ao varejo (PMC/PF) varia por
-- classe terapeutica, laboratorio ou tipo de produto?
--
-- Resposta: nao. O fator PMC/PF assume basicamente tres valores, e o unico
-- determinante e a lista de credito tributario PIS/COFINS. Esta query existe
-- justamente para documentar um caminho analitico que NAO tem sinal -- a
-- alternativa era publicar graficos de uma constante.

select
    s.lista_pis_cofins,
    count(*)                            as qtd,
    round(median(p.fator_pmc_pf), 4)    as fator_mediano,
    round(min(p.fator_pmc_pf), 4)       as fator_min,
    round(max(p.fator_pmc_pf), 4)       as fator_max
from main_marts.fct_preco p
join main_marts.fct_produto_snapshot s
  using (sk_produto, snapshot_date)
where p.aliquota_icms = 18
  and not p.area_livre_comercio
  and p.pmc is not null
group by 1
order by qtd desc;


-- O fator tambem nao muda entre faixas de ICMS: PF e PMC escalam juntos.
-- Em % a margem e identica em todo estado; so o valor em R$ muda.
select
    aliquota_icms,
    round(median(fator_pmc_pf), 4) as fator_mediano
from main_marts.fct_preco
where not area_livre_comercio and pmc is not null
group by 1
order by 1;
