import os
import sys
from PyQt5 import uic, QtWidgets
import mysql.connector
import pandas as pd
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QInputDialog
from datetime import datetime


numero_id = 0 # usar em qualquer função

caminho_controle_ui = r"C:\Users\gabriel.ribeiro\OneDrive - Moovi Comunicação e meios de pagamento EIRELI\Área de Trabalho\Projeto"
caminho_editar_produto_ui = r"C:\Users\gabriel.ribeiro\OneDrive - Moovi Comunicação e meios de pagamento EIRELI\Área de Trabalho\Projeto\editar_produto.ui"
caminho_lista_ui = r"C:\Users\gabriel.ribeiro\OneDrive - Moovi Comunicação e meios de pagamento EIRELI\Área de Trabalho\Projeto\lista.ui"
caminho_saida_ui = r"C:\Users\gabriel.ribeiro\OneDrive - Moovi Comunicação e meios de pagamento EIRELI\Área de Trabalho\Projeto\saida.ui"
caminho_estoque_ui = r"C:\Users\gabriel.ribeiro\OneDrive - Moovi Comunicação e meios de pagamento EIRELI\Área de Trabalho\Projeto\estoque.ui"
banco = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "controle_estoque",
    "port": 3306,
}

app = QtWidgets.QApplication(sys.argv)  # Cria a instância de QApplication

# Estabelece a conexão
conn = mysql.connector.connect(
    user=banco["user"],
    password=banco["password"],
    host=banco["host"],
    database=banco["database"],
    port=banco["port"],
)

# Função para obter o nome do produto pelo ID na tabela produtos
def obter_nome_produto_por_id(produto_id):
    cursor = conn.cursor()
    cursor.execute("SELECT produto FROM produtos WHERE id = %s", (produto_id,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else ''

def estoque():
    try:
        # Obter os produtos e a quantidade total no estoque
        cursor = conn.cursor()
        cursor.execute("""
            SELECT produto, COALESCE(SUM(quantidade), 0) as quantidade_saida, COALESCE(SUM(quantidade_compra), 0) as quantidade_compra
            FROM produtos
            GROUP BY produto
        """)

        # Recupere os dados e preencha a tabela de estoque
        estoque_data = cursor.fetchall()

        tela_estoque.tableWidget.setRowCount(len(estoque_data))
        tela_estoque.tableWidget.setColumnCount(2)  # Número de colunas

        for i, (produto, quantidade_saida, quantidade_compra) in enumerate(estoque_data):
            quantidade_total = quantidade_saida if quantidade_saida is not None and quantidade_saida > 0 else quantidade_compra
            tela_estoque.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(produto))
            tela_estoque.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(quantidade_total)))

        # Mostre a tela_estoque
        tela_estoque.show()

    except Exception as e:
        print("Erro ao abrir a tela de estoque:", e)

    except Exception as e:
        print("Erro ao abrir a tela de estoque:", e)


def historico_saida():
    try:
        # Consulta o histórico de saída de equipamentos no banco de dados
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hs.id, hs.produto, hs.quantidade_saida, DATE_FORMAT(hs.data_saida, '%d-%m-%Y'), hs.usuario, hs.produto_id, p.produto 
            FROM historico_saida hs 
            INNER JOIN produtos p ON p.id = hs.produto_id 
            ORDER BY hs.data_saida DESC
        """)

        historico = cursor.fetchall()

        # Consumir todos os resultados antes de prosseguir
        cursor.fetchall()

        if not historico:
            print("Histórico de saída não encontrado.")
            return

        # Preenche a tabela de histórico de saída
        tela_saida.tableWidget.setRowCount(len(historico))
        tela_saida.tableWidget.setColumnCount(6)  # Número de colunas 

        for i in range(len(historico)):
            for j in range(6):  # Número de colunas 
                item = str(historico[i][j])
                tela_saida.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(item))

        # Mostre a tela_saida
        tela_saida.show()

    except Exception as e:
        print("Erro ao abrir o histórico de saída:", e)


def saida_equipamento():
    try:
        # Obtém o ID da linha selecionada na tabela tela_lista
        linha = tela_lista.tableWidget.currentRow()
        valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

        cursor = conn.cursor()
        cursor.execute("SELECT quantidade, quantidade_compra, produto FROM produtos WHERE id = %s", (valor_id,))
        resultado_produto = cursor.fetchone()

        if resultado_produto:
            quantidade_atual, quantidade_compra, produto = resultado_produto
        else:
            print("Produto não encontrado.")
            return

        # Verifica se a quantidade_compra é nula
        if quantidade_compra is None:
            quantidade_compra = 0

        # Se a quantidade_atual for nula, inicializa com a quantidade_compra
        if quantidade_atual is None:
            quantidade_atual = quantidade_compra

        # Solicita a quantidade de saída
        quantidade_saida, ok = QInputDialog.getInt(
            tela_lista, "Quantidade de Saída", "Informe a quantidade de saída:"
        )

        if ok and quantidade_saida > 0 and quantidade_saida <= quantidade_atual:
            destinatario, ok_destinatario = QInputDialog.getText(
                tela_lista, "Destinatário", "Informe o destinatário do equipamento:"
            )

            if ok_destinatario:
                data_saida, ok_data_saida = QInputDialog.getText(
                    tela_lista,
                    "Data de Saída",
                    "Informe a data de saída (formato: DD/MM/YYYY):",
                )

                if ok_data_saida and data_saida.strip() != "":
                    try:
                        # Converte a data de saída para o formato do banco de dados (YYYY-MM-DD)
                        data_saida_formatada = datetime.strptime(
                            data_saida, "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")

                        # Inicia a transação
                        conn.start_transaction()

                        # Inserção na tabela historico_saida com o produto_id recuperado
                        cursor.execute(
                            "INSERT INTO historico_saida (produto, quantidade_saida, data_saida, usuario, produto_id) VALUES (%s, %s, %s, %s, %s)",
                            (produto, quantidade_saida, data_saida_formatada, destinatario, valor_id),
                        )

                        # Obtém o último ID inserido na tabela historico_saida
                        historico_id = cursor.lastrowid

                        # Inserção no log de transações
                        cursor.execute(
                            "INSERT INTO log_transacoes (tipo_operacao, descricao_operacao) VALUES (%s, %s)",
                            ('Saída de Equipamento', f'Saída de {quantidade_saida} unidades do produto {produto} para {destinatario}.'),
                        )

                        # Atualização do estoque na tabela produtos
                        nova_quantidade = quantidade_atual - quantidade_saida
                        cursor.execute(
                            "UPDATE produtos SET quantidade = %s WHERE id = %s",
                            (nova_quantidade, valor_id),
                        )

                        # Inserção no log de transações
                        cursor.execute(
                            "INSERT INTO log_transacoes (tipo_operacao, descricao_operacao) VALUES (%s, %s)",
                            ('Atualização de Estoque', f'Estoque do produto {produto} atualizado para {nova_quantidade}.'),
                        )

                        # Finaliza a transação
                        conn.commit()

                        print(f"{quantidade_saida} unidades foram retiradas do estoque.")
                        print(f"Quantidade atualizada: {nova_quantidade}")

                        # Atualize a lista de produtos após a saída
                        listar_produtos()

                    except ValueError as ve:
                        print(f"Erro ao converter valor: {ve}")
                        conn.rollback()
                    except mysql.connector.Error as err:
                        print(f"Erro no banco de dados: {err}")
                        conn.rollback()
                    except Exception as e:
                        print(f"Erro inesperado: {e}")
                        conn.rollback()
                else:
                    print("Data de saída não informada.")
                    # Reverta a transação em caso de erro
                    conn.rollback()
            else:
                print("Destinatário não informado.")
                # Reverta a transação em caso de erro
                conn.rollback()
        else:
            print("Quantidade inválida ou estoque insuficiente.")
            # Reverta a transação em caso de erro
            conn.rollback()

    except ValueError as ve:
        print(f"Erro ao converter valor: {ve}")
        conn.rollback()
    except mysql.connector.Error as err:
        print(f"Erro no banco de dados: {err}")
        conn.rollback()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        conn.rollback()


def editar_produtos():
    global numero_id
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (valor_id,))
    produto = cursor.fetchone()
    
    # Verifica se a tupla produto tem pelo menos 9 elementos antes de tentar acessar o nono elemento
    if produto and len(produto) >= 8:
        tela_editar.show()
        numero_id = valor_id

        tela_editar.lineEdit.setText(str(produto[0]))
        tela_editar.lineEdit_2.setText(str(produto[1]))
        tela_editar.lineEdit_3.setText(str(produto[2]))
        tela_editar.lineEdit_4.setText(str(produto[3]))
        tela_editar.lineEdit_5.setText(str(produto[4]))
        tela_editar.lineEdit_6.setText(str(produto[5]))
        tela_editar.lineEdit_7.setText(str(produto[6]))
        tela_editar.lineEdit_8.setText(str(produto[7]))
        
        # bloqueia a edição da coluna
        tela_editar.lineEdit_7.setDisabled(True)
        tela_editar.lineEdit.setDisabled(True)
        tela_editar.lineEdit_8.setDisabled(True)
    else:
        print("Erro ao obter informações do produto para edição.")


def salvar_edicao():
    global numero_id
    try:
        linha = tela_lista.tableWidget.currentRow()
        valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

        produto = tela_editar.lineEdit_2.text()
        descricao = tela_editar.lineEdit_3.text()
        preco = tela_editar.lineEdit_4.text()
        categoria = tela_editar.lineEdit_5.text()
        data = tela_editar.lineEdit_6.text()
        quantidade_compra = tela_editar.lineEdit_7.text()
        quantidade = tela_editar.lineEdit_8.text()

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produtos SET produto = %s, descricao = %s, preco = %s, categoria = %s, data = %s, quantidade_compra = %s, quantidade = %s WHERE id = %s",
            (produto, descricao, preco, categoria, data, quantidade_compra, quantidade, numero_id)
        )

        # Inserção no log de transações usando o ID do produto
        cursor.execute(
            "INSERT INTO log_transacoes (tipo_operacao, id_produto, descricao_operacao) VALUES (%s, %s, %s)",
            ('Edição de Produto', numero_id, f'Produto {numero_id} editado.')
        )

        tela_editar.close()
        tela_lista.close()
        listar_produtos()

    except mysql.connector.Error as err:
        print(f"Erro no banco de dados: {err}")
        conn.rollback()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        conn.rollback()


def excluir_produtos():
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    # diálogo de mensagem de confirmação
    confirmacao = QtWidgets.QMessageBox.question(
        tela_lista,
        "Confirmar Exclusão",
        "Tem certeza que deseja excluir o produto?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
    )

    if confirmacao == QtWidgets.QMessageBox.Yes:
        tela_lista.tableWidget.removeRow(linha)

        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = %s", (valor_id,))
        conn.commit()
        print("Produto excluído com sucesso.")
    else:
        print("Exclusão cancelada.")


def exportar_historico_compra_xlsx():
    cursor = conn.cursor()
    comando_SQL = "SELECT * FROM produtos"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    dados_lidos = pd.DataFrame(
        dados_lidos,
        columns=[
            "ID",
            "PRODUTO",
            "DESCRIÇÃO",
            "PREÇO",
            "CATEGORIA",
            "DATA",
            "QUANTIDADE_COMPRA",
            "QUANTIDADE_ATUAL"
        ],
    )
    dados_lidos.to_excel("produtos.xlsx", index=False)

    print("RELATORIO GERADO COM SUCESSO!")

def exportar_estoque_xlsx():
    try:
        # Obter os produtos e a quantidade total diretamente da tabela produtos
        cursor = conn.cursor()
        cursor.execute("SELECT produto, COALESCE(SUM(quantidade_compra), 0) as quantidade_total FROM produtos GROUP BY produto")
        estoque_data = cursor.fetchall()

        # Criar um DataFrame Pandas com os dados do estoque
        estoque_data_df = pd.DataFrame(
            estoque_data,
            columns=["Produto", "Quantidade"],
        )

        # Salvar o DataFrame no arquivo Excel 
        estoque_data_df.to_excel("estoque.xlsx", index=False)

        print("Relatório de estoque gerado com sucesso!")

    except Exception as e:
        print(f"Erro ao exportar relatório de estoque: {e}")


def registrar_produtos():
    try:
        linha1 = controle.lineEdit.text()
        linha2 = controle.lineEdit_2.text()
        linha3 = controle.lineEdit_3.text()
        linha4 = controle.dateEdit.date().toString(Qt.ISODate)  # Obtenha corretamente a data
        linha5 = controle.spinBox.value()

        categoria = ""

        if controle.radioButton.isChecked():
            print("Categoria Computador foi selecionada")
            categoria = "Computador"
        elif controle.radioButton_2.isChecked():
            print("Categoria Telefone foi selecionada")
            categoria = "Telefone"
        elif controle.radioButton_3.isChecked():
            print("Categoria Acessórios foi selecionada")
            categoria = "Acessórios"

        if linha1 and linha2 and linha3 and categoria and linha4 and linha5:
            cursor = conn.cursor()
            comando_SQL = "INSERT INTO produtos (produto, descricao, preco, categoria, data, quantidade_compra) VALUES (%s, %s, %s, %s, %s, %s)"
            dados = (str(linha1), str(linha2), str(linha3), categoria, str(linha4), str(linha5))
            cursor.execute(comando_SQL, dados)
            conn.commit()
            controle.lineEdit.setText("")
            controle.lineEdit_2.setText("")
            controle.lineEdit_3.setText("")
            controle.dateEdit.setDate(QDate(2023, 1, 1))
            controle.spinBox.setValue(0)
        else:
            QtWidgets.QMessageBox.critical(controle, "Erro", "Todos os campos devem ser preenchidos.")
    except Exception as e:
        print(f"Erro ao registrar produtos: {e}")


def listar_produtos():
    tela_lista.show()

    cursor = conn.cursor()
    comando_SQL = "SELECT * FROM produtos ORDER BY data DESC"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    tela_lista.tableWidget.setRowCount(len(dados_lidos))
    tela_lista.tableWidget.setColumnCount(8)  # Ajuste o número de colunas

    for i in range(0, len(dados_lidos)):
        for j in range(0, 8):  # Ajuste o número de colunas
            item = str(dados_lidos[i][j])
            
            # Formate a data no formato desejado (dd-mm-aaaa)
            if j == 5:  # Assumindo que a coluna correspondente à data é a sexta (índice 5)
                data_formatada = formatar_data(item)
                tela_lista.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(data_formatada))
            else:
                tela_lista.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(item))

# Função para formatar a data
def formatar_data(data):
    if data:
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d")
            return data_obj.strftime("%d-%m-%Y")
        except ValueError as e:
            print(f"Erro ao formatar data: {e}")
    return ""

controle = uic.loadUi(caminho_controle_ui + r"\controle.ui")
tela_lista = uic.loadUi(caminho_lista_ui)
tela_editar = uic.loadUi(caminho_editar_produto_ui)
tela_saida = uic.loadUi(caminho_saida_ui)
tela_estoque = uic.loadUi(caminho_estoque_ui)

controle.pushButton.clicked.connect(registrar_produtos)
controle.pushButton_2.clicked.connect(listar_produtos)
tela_lista.pushButton_2.clicked.connect(excluir_produtos)
tela_lista.pushButton_3.clicked.connect(editar_produtos)
tela_editar.pushButton.clicked.connect(salvar_edicao)
tela_lista.pushButton.clicked.connect(exportar_historico_compra_xlsx)
tela_estoque.pushButton.clicked.connect(exportar_estoque_xlsx)
tela_lista.pushButton_4.clicked.connect(saida_equipamento)
controle.pushButton_4.clicked.connect(historico_saida)
controle.pushButton_3.clicked.connect(estoque)

# janelas maximizadas
controle.setWindowState(Qt.WindowMaximized)
tela_lista.setWindowState(Qt.WindowMaximized)
tela_saida.setWindowState(Qt.WindowMaximized)

controle.show()
app.exec()
sys.exit(app.exec_())