"""Gera as fixtures de CI a partir das planilhas reais em data/raw/.

Por que fixtures: o CI nao pode depender da pagina da Anvisa. Ela serve apenas a
competencia vigente, muda o nome do arquivo a cada publicacao e um push nao pode
quebrar porque um orgao publico republicou. As fixtures deixam o CI deterministico
-- ele valida a LOGICA do pipeline, nao a disponibilidade do site.

O download real continua existindo e roda no workflow agendado (refresh.yml).

Rodar (precisa das planilhas reais em data/raw/):
    python tests/make_fixtures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import RAW_DIR, SOURCES  # noqa: E402

DESTINO = Path(__file__).parent / "fixtures"
LINHAS_DADOS = 800  # amostra suficiente para exercitar todos os testes dbt


def gerar(arquivo: str) -> Path:
    origem = RAW_DIR / arquivo
    engine = "xlrd" if origem.suffix == ".xls" else "openpyxl"
    bruto = pd.read_excel(origem, header=None, engine=engine, dtype=object)

    # Preserva o preambulo de notas + a linha de cabecalho. E justamente essa
    # parte que o parser precisa atravessar, entao ela nao pode ser cortada.
    cabecalho = bruto.iloc[: _linha_cabecalho(bruto) + 1]
    dados = bruto.iloc[_linha_cabecalho(bruto) + 1 :]

    # Amostra deterministica: primeiras + ultimas linhas. Mantem o produto de
    # GGREM duplicado e os precos com asterisco, que sao o alvo dos testes.
    amostra = pd.concat([dados.head(LINHAS_DADOS // 2), dados.tail(LINHAS_DADOS // 2)])

    saida = DESTINO / (origem.stem + ".xlsx")
    pd.concat([cabecalho, amostra]).to_excel(saida, index=False, header=False)
    print(f"{origem.name} -> {saida.name} ({saida.stat().st_size / 1e3:.0f} KB)")
    return saida


def _linha_cabecalho(bruto: pd.DataFrame) -> int:
    for idx, valor in bruto.iloc[:, 0].items():
        if str(valor).strip().upper().startswith("SUBST"):
            return int(idx)
    raise ValueError("cabecalho nao encontrado")


if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        gerar(source["file"])
