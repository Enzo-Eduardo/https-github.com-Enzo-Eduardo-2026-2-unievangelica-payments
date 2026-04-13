#!/usr/bin/env python3
"""
Testes de INTEGRAÇÃO — Módulo Carrinho (SQLite :memory:)
Aula 11 — Teste de Software (2026.1) | UniCode UniEvangelica

=======================================================================
⚠️  POR QUE ESTE ARQUIVO É DIFERENTE DE test_pagamentos.py?
=======================================================================

  test_pagamentos.py       →  TESTE UNITÁRIO
  ─────────────────────       ─────────────────────────────────────────
  • Testa funções puras       • Sem banco de dados real
  • Usa Stubs/Mocks            • Sem rede, sem arquivo externo
  • Rápido: < 1ms por teste   • Isola a LÓGICA de negócio

  test_carrinho_integracao.py →  TESTE DE INTEGRAÇÃO
  ────────────────────────────   ──────────────────────────────────────
  • Testa módulo + banco real  • SQLite real (em memória)
  • Sem Mocks — toca o banco!  • Verifica PERSISTÊNCIA dos dados
  • Um pouco mais lento        • Isola via fixture (banco novo p/ cada teste)

=======================================================================
"""

import sqlite3
import pytest
import sys
import os

# Garante que o pacote 'app' é encontrado independente de onde o aluno rodar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.carrinho_db import (
    criar_tabela,
    adicionar_item,
    listar_itens,
    calcular_total,
    limpar_carrinho,
)


# =====================================================================
# FIXTURE — Banco de dados isolado por teste
# =====================================================================

@pytest.fixture
def db():
    """
    Fixture que entrega uma conexão SQLite ':memory:' com a tabela
    'carrinho' já criada.

    O banco EM MEMÓRIA é:
      ✅ Criado do zero antes de cada teste (setup)
      ✅ Destruído automaticamente ao fim de cada teste (teardown)
      ✅ Completamente isolado — um teste não suja o outro

    Isso substitui o papel do Mock/Stub no teste unitário:
    em vez de fingir o banco, usamos um banco REAL e descartável.
    """
    conn = sqlite3.connect(":memory:")   # banco vive apenas na RAM
    criar_tabela(conn)                   # cria a estrutura da tabela
    yield conn                           # entrega para o teste
    conn.close()                         # teardown: banco destruído aqui


# =====================================================================
# GRUPO 1 — Testes de Inserção e Persistência
# =====================================================================

class TestAdicionarItem:
    """Verifica que os dados inseridos realmente ficam no banco."""

    def test_adicionar_item_retorna_id_inteiro_positivo(self, db):
        # Arrange + Act: insere um item e captura o id retornado
        item_id = adicionar_item(db, "Notebook UniPay", 3500.00, 1)

        # Assert: o id deve ser um inteiro maior ou igual a 1
        assert isinstance(item_id, int)
        assert item_id >= 1

    def test_item_persiste_com_dados_corretos(self, db):
        # Arrange
        adicionar_item(db, "Mouse Gamer", 89.90, 2)

        # Act: recupera os itens do banco real
        itens = listar_itens(db)

        # Assert: o item está lá com os dados corretos
        assert len(itens) == 1
        assert itens[0]["nome"] == "Mouse Gamer"
        assert itens[0]["preco"] == 89.90
        assert itens[0]["quantidade"] == 2

    def test_multiplos_itens_persistem_independentes(self, db):
        # Arrange: insere 3 itens distintos
        adicionar_item(db, "Teclado", 150.00, 1)
        adicionar_item(db, "Monitor", 800.00, 2)
        adicionar_item(db, "Webcam", 250.00, 1)

        # Act
        itens = listar_itens(db)

        # Assert: exatamente 3 itens no banco
        assert len(itens) == 3

    def test_ids_sao_unicos_e_sequenciais(self, db):
        # Arrange + Act
        id1 = adicionar_item(db, "Produto A", 10.00, 1)
        id2 = adicionar_item(db, "Produto B", 20.00, 1)
        id3 = adicionar_item(db, "Produto C", 30.00, 1)

        # Assert: IDs distintos e crescentes (autoincrement)
        assert id1 < id2 < id3

    def test_preco_negativo_lanca_value_error(self, db):
        # Assert: ValueError deve ser lançado ANTES de tocar o banco
        with pytest.raises(ValueError, match="negativo"):
            adicionar_item(db, "Produto Inválido", -0.01, 1)

        # Garante que o banco permanece limpo após o erro
        assert listar_itens(db) == []

    def test_quantidade_zero_lanca_value_error(self, db):
        with pytest.raises(ValueError, match="zero"):
            adicionar_item(db, "Produto Inválido", 100.00, 0)

    def test_quantidade_negativa_lanca_value_error(self, db):
        with pytest.raises(ValueError):
            adicionar_item(db, "Produto Inválido", 100.00, -5)


# =====================================================================
# GRUPO 2 — Testes de Cálculo de Total
# =====================================================================

class TestCalcularTotal:
    """Verifica o cálculo de SUM(preco * quantidade) no banco real."""

    def test_carrinho_vazio_retorna_zero(self, db):
        # Arrange: nada foi inserido (banco vazio)
        # Act
        total = calcular_total(db)
        # Assert
        assert total == 0.0

    def test_total_item_unico_sem_desconto(self, db):
        # Arrange
        adicionar_item(db, "Headset", 200.00, 1)
        # Act
        total = calcular_total(db)
        # Assert
        assert total == 200.0

    def test_total_considera_quantidade(self, db):
        # Arrange: 3 unidades × R$ 50,00 = R$ 150,00
        adicionar_item(db, "Caneta", 50.00, 3)
        # Act
        total = calcular_total(db)
        # Assert: banco calculou preco * quantidade
        assert total == 150.0

    def test_total_multiplos_itens_soma_correta(self, db):
        # Arrange
        adicionar_item(db, "Item A", 100.00, 2)   # subtotal: 200.00
        adicionar_item(db, "Item B",  50.00, 1)   # subtotal:  50.00
        adicionar_item(db, "Item C",  75.00, 4)   # subtotal: 300.00

        # Act
        total = calcular_total(db)

        # Assert: 200 + 50 + 300 = 550
        assert total == 550.0

    def test_total_com_centavos_e_precisao_float(self, db):
        # Cenário realista: valores com casas decimais
        adicionar_item(db, "Produto R", 99.99, 3)   # 299.97
        adicionar_item(db, "Produto S", 0.01, 3)    #   0.03
        total = calcular_total(db)
        # 299.97 + 0.03 = 300.00 (sem arredondamento absurdo)
        assert round(total, 2) == 300.00


# =====================================================================
# GRUPO 3 — Testes de Limpeza do Carrinho
# =====================================================================

class TestLimparCarrinho:
    """Verifica a operação de DELETE e seu impacto no total."""

    def test_limpar_remove_todos_os_itens(self, db):
        # Arrange
        adicionar_item(db, "Produto 1", 10.00, 1)
        adicionar_item(db, "Produto 2", 20.00, 1)

        # Act
        rows_deletadas = limpar_carrinho(db)

        # Assert: 2 linhas foram removidas e lista está vazia
        assert rows_deletadas == 2
        assert listar_itens(db) == []

    def test_limpar_carrinho_vazio_retorna_zero(self, db):
        # Arrange: carrinho já está vazio
        # Act
        rows_deletadas = limpar_carrinho(db)
        # Assert: DELETE sem linhas → rowcount == 0
        assert rows_deletadas == 0

    def test_total_apos_limpar_e_zero(self, db):
        # Arrange: adiciona e limpa
        adicionar_item(db, "Produto Caro", 9999.00, 5)
        limpar_carrinho(db)

        # Act
        total = calcular_total(db)

        # Assert: COALESCE garante 0.0 mesmo com tabela vazia
        assert total == 0.0

    def test_pode_adicionar_apos_limpar(self, db):
        # Arrange: ciclo completo — adiciona, limpa, adiciona de novo
        adicionar_item(db, "Ciclo 1", 100.00, 1)
        limpar_carrinho(db)
        adicionar_item(db, "Ciclo 2", 200.00, 1)

        # Act
        itens = listar_itens(db)
        total = calcular_total(db)

        # Assert: somente o segundo item existe
        assert len(itens) == 1
        assert itens[0]["nome"] == "Ciclo 2"
        assert total == 200.0
