import os
from PyQt5 import uic, QtWidgets
import mysql.connector
import pandas as pd
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt

numero_id = 0

caminho_controle_ui = r"C:digite o caminho"
caminho_editar_produto_ui = r"C:digite o caminho"
caminho_lista_ui = r"C:digite o caminho"

banco = {
    "user": "seu root",
    "password": "senha",
    "host": "localhost",
    "database": "controle_estoque",
    "port": 3306,
}
# Estabelece a conexão
conn = mysql.connector.connect(
    user=banco["user"],
    password=banco["password"],
    host=banco["host"],
    database=banco["database"],
    port=banco["port"],
)


def saida_equipamento():
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = %s", (valor_id,))
    quantidade_atual = cursor.fetchone()[0]

    quantidade_saida, ok = QtWidgets.QInputDialog.getInt(
        tela_lista, "Quantidade de Saída", "Informe a quantidade de saída:"
    )

    if ok:
        if quantidade_saida > 0 and quantidade_saida <= quantidade_atual:
            nova_quantidade = quantidade_atual - quantidade_saida
            cursor.execute(
                "UPDATE produtos SET quantidade = %s WHERE id = %s",
                (nova_quantidade, valor_id),
            )
            conn.commit()
            listar_produtos()
            print(f"{quantidade_saida} unidades foram retiradas do estoque.")
        else:
            print("Quantidade inválida ou estoque insuficiente.")


def editar_produtos():
    global numero_id
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (valor_id,))
    produto = cursor.fetchone()
    tela_editar.show()

    numero_id = valor_id

    tela_editar.lineEdit.setText(str(produto[0]))
    tela_editar.lineEdit_2.setText(str(produto[1]))
    tela_editar.lineEdit_3.setText(str(produto[2]))
    tela_editar.lineEdit_4.setText(str(produto[3]))
    tela_editar.lineEdit_5.setText(str(produto[4]))
    tela_editar.lineEdit_6.setText(str(produto[5]))
    tela_editar.lineEdit_7.setText(str(produto[6]))

    # bloqueia a edição da coluna
    tela_editar.lineEdit_7.setDisabled(True)
    tela_editar.lineEdit.setDisabled(True)


def salvar_edicao():
    global numero_id
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    produto = tela_editar.lineEdit_2.text()
    descricao = tela_editar.lineEdit_3.text()
    preco = tela_editar.lineEdit_4.text()
    categoria = tela_editar.lineEdit_5.text()
    data = tela_editar.lineEdit_6.text()
    quantidade = tela_editar.lineEdit_7.text()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET produto = '{}', descricao = '{}', preco = '{}', categoria ='{}', data = '{}', quantidade = '{}' WHERE id = {}".format(
            produto, descricao, preco, categoria, data, quantidade, numero_id
        )
    )

    tela_editar.close()
    tela_lista.close()
    listar_produtos()


def excluir_produtos():
    linha = tela_lista.tableWidget.currentRow()
    valor_id = int(tela_lista.tableWidget.item(linha, 0).text())

    # Mostra um diálogo de mensagem de confirmação
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


def exportar_xlsx():
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
            "QUANTIDADE",
        ],
    )
    dados_lidos.to_excel("produtos.xlsx", index=False)

    print("RELATORIO GERADO COM SUCESSO!")


def registrar_produtos():
    linha1 = controle.lineEdit.text()
    linha2 = controle.lineEdit_2.text()
    linha3 = controle.lineEdit_3.text()
    linha4 = controle.dateEdit.text()
    linha5 = controle.spinBox.value()

    categoria = ""

    if controle.radioButton.isChecked():
        print("Categoria Computador foi selecionado")
        categoria = "Computador"
    elif controle.radioButton_2.isChecked():
        print("Categoria Telefone foi selecionado")
        categoria = "Telefone"
    elif controle.radioButton_3.isChecked():
        print("Categoria Acessórios foi selecionado")
        categoria = "Acessórios"

    if linha1 and linha2 and linha3 and categoria and linha4 and linha5:
        cursor = conn.cursor()
        comando_SQL = "INSERT INTO produtos (produto,descricao,preco,categoria,data,quantidade) VALUES (%s,%s,%s,%s,%s,%s)"
        dados = (
            str(linha1),
            str(linha2),
            str(linha3),
            categoria,
            str(linha4),
            str(linha5),
        )
        cursor.execute(comando_SQL, dados)
        conn.commit()
        controle.lineEdit.setText("")
        controle.lineEdit_2.setText("")
        controle.lineEdit_3.setText("")
        controle.dateEdit.setDate(QDate(2023, 1, 1))
        controle.spinBox.setValue(0)
    else:
        QtWidgets.QMessageBox.critical(
            controle, "Erro", "Todos os campos devem ser preenchidos."
        )


def listar_produtos():
    tela_lista.show()

    cursor = conn.cursor()
    comando_SQL = "SELECT * FROM produtos ORDER BY data DESC"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    tela_lista.tableWidget.setRowCount(len(dados_lidos))
    tela_lista.tableWidget.setColumnCount(7)  # Ajuste o número de colunas

    for i in range(0, len(dados_lidos)):
        for j in range(0, 7):  # Ajuste o número de colunas
            item = str(dados_lidos[i][j])
            tela_lista.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(item))


app = QtWidgets.QApplication([])
controle = uic.loadUi(caminho_controle_ui + r"\controle.ui")
tela_lista = uic.loadUi(caminho_lista_ui)
tela_editar = uic.loadUi(caminho_editar_produto_ui)
controle.pushButton.clicked.connect(registrar_produtos)
controle.pushButton_2.clicked.connect(listar_produtos)
tela_lista.pushButton_2.clicked.connect(excluir_produtos)
tela_lista.pushButton_3.clicked.connect(editar_produtos)
tela_editar.pushButton.clicked.connect(salvar_edicao)
tela_lista.pushButton.clicked.connect(exportar_xlsx)
tela_lista.pushButton_4.clicked.connect(saida_equipamento)

#janelas maximizadas
controle.setWindowState(Qt.WindowMaximized)
tela_lista.setWindowState(Qt.WindowMaximized)


controle.show()
app.exec()
