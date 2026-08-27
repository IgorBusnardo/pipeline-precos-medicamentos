"""Resolve e baixa a lista de precos CMED vigente.

A Anvisa publica apenas a competencia atual, e o nome do arquivo carrega um
timestamp que muda a cada publicacao. Nao ha URL estavel por competencia, entao
o link e resolvido a partir da pagina em vez de ficar fixo no codigo.
Competencias antigas nao sao recuperaveis por aqui -- devem estar em data/raw/.
"""
from __future__ import annotations

import logging
import re
import urllib.parse
import urllib.request

from config import DOWNLOAD_LINK_PATTERN, RAW_DIR, SOURCE_PAGE, SOURCES

log = logging.getLogger(__name__)
UA = {"User-Agent": "cmed-pipeline (https://github.com)"}


def resolver_link_vigente() -> str:
    req = urllib.request.Request(SOURCE_PAGE, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    match = re.search(DOWNLOAD_LINK_PATTERN, html)
    if not match:
        raise RuntimeError(
            f"link da lista nao encontrado em {SOURCE_PAGE}. "
            "A Anvisa mudou o layout da pagina -- ajuste DOWNLOAD_LINK_PATTERN em src/config.py."
        )
    return urllib.parse.urljoin(SOURCE_PAGE, match.group(0))


def run() -> list:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    faltando = [s["file"] for s in SOURCES if not (RAW_DIR / s["file"]).exists()]
    if not faltando:
        log.info("todas as competencias declaradas ja estao em data/raw/")
        return []

    url = resolver_link_vigente()
    destino = RAW_DIR / url.split("/")[-3]
    log.info("baixando competencia vigente: %s", url)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as resp, open(destino, "wb") as fh:
        fh.write(resp.read())
    log.info("gravado %s (%.1f MB)", destino.name, destino.stat().st_size / 1e6)

    log.warning(
        "competencias ausentes que a pagina NAO serve: %s. "
        "Baixe manualmente em %s e coloque em data/raw/.",
        ", ".join(faltando), SOURCE_PAGE,
    )
    return [destino]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
