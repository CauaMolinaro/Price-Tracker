def _criar_produto(client):
    return client.post(
        "/produtos/",
        json={"nome": "RTX 4070", "url": "https://exemplo.com/rtx4070", "loja": "kabum"},
    ).json()


def test_registrar_e_consultar_historico(client):
    produto = _criar_produto(client)

    resposta = client.post(f"/precos/{produto['id']}?preco=2999.90")
    assert resposta.status_code == 201

    historico = client.get(f"/precos/{produto['id']}/historico").json()
    assert len(historico) == 1
    assert historico[0]["preco"] == 2999.90


def test_registrar_preco_produto_inexistente(client):
    resposta = client.post("/precos/999?preco=100")
    assert resposta.status_code == 404


def test_criar_alerta(client):
    produto = _criar_produto(client)

    resposta = client.post(
        "/alertas/",
        json={"produto_id": produto["id"], "preco_alvo": 2500.0, "email": "user@exemplo.com"},
    )
    assert resposta.status_code == 201
    assert resposta.json()["disparado"] is False
