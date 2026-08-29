"""
Scraper de preços.

Este módulo é responsável por buscar o preço atual de um produto em
uma página web e devolver o valor em float. Cada loja tem um "parser"
próprio, já que o HTML muda de site pra site.

Para rodar de verdade contra um site, ajuste o seletor CSS/estrutura
em `_parse_kabum` (ou crie um novo parser) de acordo com o HTML atual
da página — sites mudam o layout com frequência.
"""
import re
import time
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def _extrair_numero(texto: str) -> float:
    """Converte 'R$ 1.299,90' em 1299.90."""
    numero = re.sub(r"[^\d,]", "", texto)
    numero = numero.replace(",", ".")
    return float(numero)


def _parse_kabum(html: str) -> float:
    soup = BeautifulSoup(html, "html.parser")
    # NOTE: seletor de exemplo — inspecione o HTML atual da página e ajuste.
    elemento = soup.select_one("h4.finalPrice")
    if not elemento:
        raise ValueError("Elemento de preço não encontrado (verifique o seletor CSS)")
    return _extrair_numero(elemento.get_text())


PARSERS = {
    "kabum": _parse_kabum,
}


def buscar_preco(url: str, loja: str, tentativas: int = 3) -> float:
    """
    Busca o preço atual de um produto.

    Faz algumas tentativas com espera progressiva antes de desistir,
    já que scraping falha por instabilidade de rede com frequência.
    """
    parser = PARSERS.get(loja.lower())
    if parser is None:
        raise ValueError(f"Nenhum parser configurado para a loja '{loja}'")

    ultima_excecao = None
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, headers=HEADERS, timeout=10)
            resposta.raise_for_status()
            return parser(resposta.text)
        except Exception as exc:  # noqa: BLE001
            ultima_excecao = exc
            logger.warning("Tentativa %d/%d falhou para %s: %s", tentativa, tentativas, url, exc)
            time.sleep(2 * tentativa)

    raise RuntimeError(f"Falha ao buscar preço de {url}") from ultima_excecao
