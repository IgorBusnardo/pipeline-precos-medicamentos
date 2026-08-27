"""Gera o grafico do README a partir das marts. Nao le a planilha: le o modelo.

Se este script precisar de qualquer limpeza de dado, a limpeza esta no lugar
errado -- ela pertence ao dbt.
"""
from __future__ import annotations

import logging

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import DUCKDB_PATH, ROOT

log = logging.getLogger(__name__)
OUT = ROOT / "docs" / "reajuste_por_faixa.png"

QUERY = """
select round(variacao_pct, 1) as reajuste_pct, count(*) as qtd
from main_marts.mart_variacao_pf
where not flag_outlier and variacao_pct between 0 and 6
group by 1
order by 1
"""


def run():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as con:
        df = con.execute(QUERY).fetchdf()

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df.reajuste_pct, df.qtd, width=0.09, color="#2b6cb0")

    for x, rotulo in [(1.1, "nível 3"), (2.4, "nível 2"), (3.7, "nível 2"), (5.1, "nível 1")]:
        alvo = df.loc[(df.reajuste_pct - x).abs().idxmin()]
        ax.annotate(f"{rotulo}\n{alvo.reajuste_pct:.1f}%",
                    xy=(alvo.reajuste_pct, alvo.qtd), xytext=(0, 10),
                    textcoords="offset points", ha="center", fontsize=9, color="#1a365d")

    ax.set_title("Reajuste de Preço Fábrica, jul/2025 → jul/2026\n"
                 "O teto CMED não é um número só: são faixas discretas",
                 fontsize=12, loc="left")
    ax.set_xlabel("reajuste aplicado (%)")
    ax.set_ylabel("apresentações")
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(y=0.15)
    fig.tight_layout()
    fig.savefig(OUT, dpi=140)
    log.info("gravado %s", OUT)
    return OUT


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
