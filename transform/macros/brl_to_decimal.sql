{#
  A CMED publica preco como texto pt-BR e ainda marca ~1.100 valores com um
  asterisco de nota de rodape ("230857,28*"). Sem tratar isso o cast retorna
  null silenciosamente e o produto some da analise.
#}
{% macro brl_to_decimal(coluna) %}
    try_cast(
        replace(
            replace(
                replace(
                    nullif(nullif(trim({{ coluna }}), '-'), ''),
                '*', ''),
            '.', ''),
        ',', '.')
        as decimal(14, 2)
    )
{% endmacro %}


{% macro sim_nao_to_bool(coluna) %}
    case
        when upper(trim({{ coluna }})) in ('SIM', 'S') then true
        when upper(trim({{ coluna }})) in ('NAO', 'NÃO', 'N') then false
    end
{% endmacro %}
