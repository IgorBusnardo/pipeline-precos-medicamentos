"""Registro das fontes CMED e caminhos do projeto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PARQUET_DIR = ROOT / "data" / "parquet"
DUCKDB_PATH = ROOT / "data" / "cmed.duckdb"

# Pagina oficial das listas de precos. Ela publica APENAS a competencia vigente,
# e o nome do arquivo carrega um timestamp que muda a cada publicacao
# (xls_conformidade_site_20260811_192510234.xlsx). Nao existe URL estavel por
# competencia: src/download.py resolve o link atual a partir desta pagina, e
# competencias antigas precisam ser colocadas em data/raw/ manualmente.
SOURCE_PAGE = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
DOWNLOAD_LINK_PATTERN = r"/anvisa/[^\"']*xls_conformidade_site_\d+\.xlsx/@@download/file"

# A competencia NAO e informada aqui: ela e lida da propria planilha, da linha
# "Publicada em DD/MM/AAAA". Assim uma competencia nova entra no pipeline so
# colocando o arquivo em data/raw/, sem editar codigo.
SOURCES = [
    {"file": "Precos_Jul_25.xls"},
    {"file": "Precos_Jul_26.xlsx"},
]

# A planilha traz ~41 linhas de notas antes do cabecalho, e o numero de linhas
# muda entre competencias. Detectamos o cabecalho por esta ancora.
HEADER_ANCHOR = "SUBSTANCIA"
HEADER_SEARCH_ROWS = 120

# Nomes longos da CMED -> nomes curtos e estaveis.
RENAME = {
    "codigo_ggrem": "ggrem",
    "tipo_de_produto_status_do_produto": "tipo_produto",
    "regime_de_preco": "regime_preco",
    "lista_de_concessao_de_credito_tributario_pis_cofins": "lista_pis_cofins",
    "restricao_hospitalar": "restricao_hospitalar",
    "icms_0": "icms_zero",
}

# Colunas descritivas que sobrevivem ao unpivot (o resto vira medida).
DIM_COLS = [
    "ggrem", "substancia", "cnpj", "laboratorio", "registro",
    "ean_1", "ean_2", "ean_3", "produto", "apresentacao",
    "classe_terapeutica", "tipo_produto", "regime_preco",
    "restricao_hospitalar", "cap", "confaz_87", "icms_zero",
    "analise_recursal", "lista_pis_cofins", "tarja", "destinacao_comercial",
    "comercializacao_ano_anterior", "ano_comercializacao",
]
