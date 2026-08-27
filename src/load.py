"""Load: Parquet -> DuckDB (schema `raw`).

Carga full-refresh. Sao ~26k linhas por competencia e duas competencias por ano:
incremental aqui seria complexidade sem ganho. A tabela e recriada a partir dos
Parquet, entao rodar duas vezes produz o mesmo resultado.
"""
from __future__ import annotations

import logging

import duckdb

from config import DUCKDB_PATH, PARQUET_DIR

log = logging.getLogger(__name__)

DDL = """
create schema if not exists raw;

create or replace table raw.cmed_precos as
select * from read_parquet($glob, union_by_name = true);
"""


def run() -> int:
    arquivos = sorted(PARQUET_DIR.glob("*.parquet"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum parquet em {PARQUET_DIR}; rode src/ingest.py antes")

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH)) as con:
        con.execute(DDL, {"glob": str(PARQUET_DIR / "*.parquet")})
        linhas, snapshots = con.execute(
            "select count(*), count(distinct snapshot_date) from raw.cmed_precos"
        ).fetchone()

    log.info("raw.cmed_precos: %s linhas em %s snapshots (%s arquivos)",
             f"{linhas:,}", snapshots, len(arquivos))
    return linhas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
