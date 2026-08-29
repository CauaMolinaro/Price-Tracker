"""
Job agendado: percorre todos os produtos cadastrados, busca o preço
atual e grava no histórico. Também verifica alertas pendentes.

Rodar manualmente:
    python -m app.scraper.job

Rodar em intervalos (ex: a cada 6 horas) usando APScheduler ou, de
forma mais simples, um cron job do sistema / GitHub Actions agendado.
"""
import logging

from app.database import SessionLocal
from app.models.models import Produto, HistoricoPreco, Alerta
from app.scraper.scraper import buscar_preco

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rodar_coleta():
    db = SessionLocal()
    try:
        produtos = db.query(Produto).all()
        logger.info("Coletando preços de %d produto(s)...", len(produtos))

        for produto in produtos:
            try:
                preco_atual = buscar_preco(produto.url, produto.loja)
            except Exception as exc:  # noqa: BLE001
                logger.error("Erro ao coletar preço de '%s': %s", produto.nome, exc)
                continue

            db.add(HistoricoPreco(produto_id=produto.id, preco=preco_atual))
            logger.info("%s -> R$ %.2f", produto.nome, preco_atual)

            _verificar_alertas(db, produto.id, preco_atual)

        db.commit()
    finally:
        db.close()


def _verificar_alertas(db, produto_id: int, preco_atual: float):
    alertas_pendentes = (
        db.query(Alerta)
        .filter(
            Alerta.produto_id == produto_id,
            Alerta.disparado.is_(False),
            Alerta.preco_alvo >= preco_atual,
        )
        .all()
    )
    for alerta in alertas_pendentes:
        # TODO: plugar envio de e-mail real (ex: smtplib ou um serviço como Resend/SendGrid)
        logger.info(
            "ALERTA disparado: produto_id=%s atingiu R$ %.2f (alvo R$ %.2f) -> notificar %s",
            produto_id,
            preco_atual,
            alerta.preco_alvo,
            alerta.email,
        )
        alerta.disparado = True


if __name__ == "__main__":
    rodar_coleta()
