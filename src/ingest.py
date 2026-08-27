"""Extract + Load: planilhas CMED -> Parquet.

Nao converte tipo de preco aqui de proposito. Os precos sao mantidos como texto,
exatamente como a CMED publicou, e o cast acontece no dbt. Assim o Parquet e
auditavel contra a planilha original e uma regra de limpeza errada nao exige
reprocessar a extracao.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime, timezone

import pandas as pd

from config import DIM_COLS, HEADER_ANCHOR, HEADER_SEARCH_ROWS, PARQUET_DIR, RAW_DIR, RENAME, SOURCES

log = logging.getLogger(__name__)


def to_snake(name: object) -> str:
    """'PF 17,5 %  ALC' -> 'pf_17_5_alc'. Remove acento e pontuacao."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def find_header_row(path, engine: str) -> int:
    """A CMED muda a quantidade de linhas de nota entre competencias.
    Procuramos a linha do cabecalho em vez de fixar um numero magico."""
    probe = pd.read_excel(path, header=None, nrows=HEADER_SEARCH_ROWS, engine=engine)
    for idx, value in probe.iloc[:, 0].items():
        if to_snake(value) == to_snake(HEADER_ANCHOR):
            return int(idx)
    raise ValueError(f"cabecalho nao encontrado em {path.name} (ancora={HEADER_ANCHOR!r})")


def find_publication_date(path, engine: str) -> "pd.Timestamp":
    """A competencia esta dentro do arquivo, na linha 'Publicada em DD/MM/AAAA'.

    Ler dali em vez de fixar a data no config significa que uma competencia nova
    entra no pipeline so colocando o arquivo em data/raw/."""
    probe = pd.read_excel(path, header=None, nrows=HEADER_SEARCH_ROWS, engine=engine)
    for value in probe.iloc[:, 0]:
        match = re.search(r"Publicada em (\d{2}/\d{2}/\d{4})", str(value))
        if match:
            return pd.to_datetime(match.group(1), format="%d/%m/%Y")
    raise ValueError(f"data de publicacao nao encontrada em {path.name}")


def resolve_schema_drift(df: pd.DataFrame) -> pd.DataFrame:
    """A coluna de comercializacao carrega o ano no proprio nome
    ('COMERCIALIZACAO 2024' -> 'COMERCIALIZACAO 2025'). Isso quebraria o schema a
    cada competencia, entao o ano vira dado (coluna) em vez de metadado (nome)."""
    for col in df.columns:
        match = re.fullmatch(r"comercializacao_(\d{4})", col)
        if match:
            df = df.rename(columns={col: "comercializacao_ano_anterior"})
            df["ano_comercializacao"] = int(match.group(1))
            return df
    df["comercializacao_ano_anterior"] = pd.NA
    df["ano_comercializacao"] = pd.NA
    return df


def read_snapshot(source: dict) -> pd.DataFrame:
    path = RAW_DIR / source["file"]
    engine = "xlrd" if path.suffix == ".xls" else "openpyxl"

    snapshot_date = pd.Timestamp(source["snapshot_date"]) if source.get("snapshot_date")         else find_publication_date(path, engine)

    header_row = find_header_row(path, engine)
    df = pd.read_excel(path, header=header_row, engine=engine, dtype=str)
    df.columns = [to_snake(c) for c in df.columns]
    df = df.rename(columns=RENAME)
    df = resolve_schema_drift(df)

    # Contrato de schema: tudo que veio da planilha e texto. Sem isso, uma
    # coluna totalmente vazia numa competencia muda de tipo no Parquet e
    # quebra a uniao com as outras.
    df = df.astype("string").apply(lambda s: s.str.strip())
    df["snapshot_date"] = snapshot_date.date()
    df["arquivo_origem"] = path.name
    df["ingerido_em"] = datetime.now(timezone.utc)

    faltando = [c for c in DIM_COLS if c not in df.columns]
    if faltando:
        raise ValueError(f"{path.name}: colunas esperadas ausentes: {faltando}")

    log.info("%s -> competencia %s, %s linhas x %s colunas (cabecalho na linha %s)",
             path.name, snapshot_date.date(), len(df), len(df.columns), header_row)
    return df


def run() -> list:
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    escritos = []
    for source in SOURCES:
        df = read_snapshot(source)
        # Nomeado pelo arquivo de origem, nao pela competencia: reprocessar
        # sobrescreve o mesmo Parquet em vez de acumular um por execucao.
        destino = PARQUET_DIR / f"{(RAW_DIR / source['file']).stem}.parquet"
        df.to_parquet(destino, index=False)
        log.info("gravado %s (%.1f MB)", destino.name, destino.stat().st_size / 1e6)
        escritos.append(destino)
    return escritos


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
