"""Orquestrador do pipeline. Sem Airflow: sao tres passos sequenciais sobre
26 mil linhas por competencia. Agendamento fica no GitHub Actions.

    python run.py            # pipeline completo
    python run.py --skip-dbt # so extract + load
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import config  # noqa: E402
import ingest  # noqa: E402
import load  # noqa: E402
import report  # noqa: E402

TRANSFORM_DIR = Path(__file__).parent / "transform"
log = logging.getLogger("pipeline")


def dbt(comando: str) -> None:
    args = ["dbt", comando, "--project-dir", str(TRANSFORM_DIR), "--profiles-dir", str(TRANSFORM_DIR)]
    env = {**os.environ, "CMED_DUCKDB": str(config.DUCKDB_PATH)}
    log.info("$ %s", " ".join(args))
    subprocess.run(args, check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-dbt", action="store_true")
    parser.add_argument("--skip-report", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(name)s | %(message)s")

    log.info("1/4 extract: planilhas CMED -> Parquet")
    ingest.run()

    log.info("2/4 load: Parquet -> DuckDB (raw)")
    load.run()

    if not args.skip_dbt:
        log.info("3/4 transform + test: dbt build")
        dbt("deps")
        dbt("build")

    if not args.skip_report:
        log.info("4/4 report: grafico do README")
        report.run()

    log.info("pipeline concluido")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
