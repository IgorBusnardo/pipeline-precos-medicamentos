"""Canario da fonte: verifica se a pagina da Anvisa ainda e parseavel.

Nao valida a logica do pipeline (isso e o CI das fixtures). Valida a premissa
externa: o link ainda e encontravel, o arquivo ainda abre, o cabecalho ainda
esta onde a ancora diz e a data de publicacao ainda esta legivel.

Roda agendado. Se falhar, a Anvisa mudou algo e o pipeline precisa de ajuste --
melhor descobrir por um job semanal que por um push que nao tem nada a ver.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import download  # noqa: E402
from ingest import find_header_row, find_publication_date  # noqa: E402


def main() -> int:
    baixados = download.run()
    if not baixados:
        print("nada baixado: as competencias declaradas ja estao em disco")
        return 0

    arquivo = baixados[0]
    engine = "xlrd" if arquivo.suffix == ".xls" else "openpyxl"

    linha = find_header_row(arquivo, engine)
    competencia = find_publication_date(arquivo, engine)

    print(f"OK {arquivo.name}: cabecalho na linha {linha}, competencia {competencia.date()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
