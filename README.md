# 📉 Price Tracker API

API REST em **Python (FastAPI)** para monitorar o histórico de preços de produtos (hardware, jogos, eletrônicos) e disparar alertas quando o preço cai abaixo de um valor alvo.

Projeto construído do zero como peça de portfólio, com foco em modelagem de banco de dados, queries SQL, design de API e boas práticas de backend.

## ✨ Funcionalidades

- **CRUD de produtos** monitorados
- **Histórico de preços** por produto, com filtro por período
- **Ranking de maiores quedas de preço** (query SQL de agregação com subqueries)
- **Sistema de alertas**: cadastra um preço-alvo e um e-mail para notificação
- **Scraper** de exemplo com retry/backoff, extensível para novas lojas
- **Job agendável** que coleta preços e verifica alertas pendentes
- Testes automatizados com **pytest**
- Pronto para rodar com **Docker / Docker Compose**

## 🏗️ Arquitetura

```
price-tracker/
├── app/
│   ├── main.py              # ponto de entrada da API
│   ├── database.py          # configuração SQLAlchemy
│   ├── models/               # modelos ORM (tabelas do banco)
│   ├── schemas/               # schemas Pydantic (validação de entrada/saída)
│   ├── routers/               # endpoints da API
│   └── scraper/               # coleta de preços + job agendável
├── tests/                    # testes automatizados (pytest)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Modelo de dados

```
Produto (1) ────< HistoricoPreco (N)
Produto (1) ────< Alerta (N)
```

- **produtos**: item monitorado (nome, url, loja)
- **historico_precos**: uma linha por coleta de preço (série temporal)
- **alertas**: preço-alvo + e-mail para notificação

## 🚀 Como rodar

### Localmente

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) em `http://localhost:8000/docs`.

### Com Docker

```bash
docker compose up --build
```

### Rodando os testes

```bash
pytest -v
```

### Rodando a coleta de preços manualmente

```bash
python -m app.scraper.job
```

## 📌 Exemplos de uso da API

**Cadastrar um produto:**
```bash
curl -X POST http://localhost:8000/produtos/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "RTX 4070", "url": "https://kabum.com.br/produto/x", "loja": "kabum"}'
```

**Consultar o histórico de preço dos últimos 30 dias:**
```bash
curl http://localhost:8000/precos/1/historico?dias=30
```

**Ver os produtos com maior queda de preço:**
```bash
curl http://localhost:8000/precos/maiores-quedas?dias=30&limite=5
```

**Criar um alerta:**
```bash
curl -X POST http://localhost:8000/alertas/ \
  -H "Content-Type: application/json" \
  -d '{"produto_id": 1, "preco_alvo": 2500.00, "email": "voce@exemplo.com"}'
```

## 🧰 Tecnologias

Python · FastAPI · SQLAlchemy · Pydantic · SQLite/PostgreSQL · pytest · BeautifulSoup · Docker

## 🔭 Próximos passos

- [ ] Autenticação (JWT) para múltiplos usuários
- [ ] Envio real de e-mail (SMTP ou serviço tipo Resend)
- [ ] Migrações com Alembic
- [ ] Deploy (Render/Railway) + CI no GitHub Actions
- [ ] Novos parsers de scraper (Amazon, Steam, Mercado Livre)

## 👤 Autor

Cauã — Estudante de Engenharia de Software (USJT)
