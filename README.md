Controle de Estoque - Aplicação PyQt5 e MySQL

Este é um projeto de controle de estoque desenvolvido em Python com a biblioteca PyQt5 para a interface gráfica e MySQL como banco de dados. A aplicação permite registrar, listar, editar e excluir produtos do estoque, além de exportar os dados para um arquivo Excel (xlsx).


*Requisitos

Python 3.x
PyQt5
mysql-connector-python
pandas
Instalação

*Certifique-se de que o Python esteja instalado em seu sistema.

Instale as bibliotecas necessárias através do comando:pip install PyQt5 mysql-connector-python pandas

*Como usar

Clone ou baixe este repositório para o seu computador.
Abra o terminal (ou prompt de comando) e navegue até a pasta do projeto.
Execute o arquivo controle_estoque.py para iniciar o aplicativo: python controle_estoque.py
A interface do aplicativo será exibida, permitindo o registro, listagem, edição e exclusão de produtos no estoque.

*Funcionalidades

Registrar Produtos: Preencha os campos na interface e clique no botão "Registrar" para adicionar um novo produto ao estoque.
Listar Produtos: Clique no botão "Listar" para visualizar todos os produtos registrados no estoque em uma tabela.
Editar Produtos: Na lista de produtos, clique em um item para selecioná-lo e, em seguida, clique no botão "Editar". Edite os campos desejados e clique em "Salvar" para atualizar as informações do produto.
Excluir Produtos: Selecione um produto na lista e clique no botão "Excluir" para remover o produto do estoque.
Exportar para Excel: Clique no botão "Exportar para Excel" para gerar um arquivo "produtos.xlsx" contendo todos os dados do estoque em formato Excel.

*Configurações do Banco de Dados

O aplicativo está configurado para se conectar a um servidor MySQL local.

Usuário: 
Senha: 
Host: 
Banco de Dados: controle_estoque
Porta: 3306

OBS:Você pode modificar essas configurações no código, caso o seu ambiente de banco de dados seja diferente. Certifique-se de que o servidor MySQL esteja em execução e acessível.
