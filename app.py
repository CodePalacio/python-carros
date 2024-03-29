import sqlite3
import os

class Carro:
    def __init__(self, nome, disponivel=True):
        self.nome = nome
        self.disponivel = disponivel

class Locadora:
    def __init__(self, nome_banco) -> None:
        self.conn = sqlite3.connect(nome_banco)
        self.c = self.conn.cursor()
        self._criar_tabela_carros()
        self._criar_tabela_carros_alugados()

    def __str__(self) -> str:
        return "{}".format(self.carros_disponiveis)
    
    def _criar_tabela_carros(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS carros (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT NOT NULL,
                       disponivel INTEGER NOT NULL
        )''')
        self.conn.commit()

    def _criar_tabela_carros_alugados(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS carros_alugados (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       carro_id INTEGER NOT NULL,
                       cliente TEXT NOT NULL,
                       FOREIGN KEY(carro_id) REFERENCES carros(id)
        )''')
        self.conn.commit()

    def adiciona_carro(self, carro):
        if not isinstance(carro, Carro):
            print(f"Erro: Você deve fornecer um objeto do tipo Carro")
            return
        try:
            self.c.execute("INSERT INTO carros (nome, disponivel) VALUES(?,?)", (carro.nome, carro.disponivel))
            self.conn.commit()
            print(f"{carro.nome} adicionado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar {carro.nome}: {e}")

    def aluga_carro(self, cliente, id):
        if not cliente:
            print("Erro: Nome do cliente nao pode estar vazio")
            return
        try:
            self.c.execute("SELECT nome FROM carros WHERE id = ? AND disponivel = 1", (id,))
            resultado = self.c.fetchone()
            if resultado: 
                self.c.execute("UPDATE carros SET disponivel = 0 WHERE id = ?", (id,))
                self.c.execute("INSERT INTO carros_alugados (carro_id, cliente) VALUES(?,?)", (id, cliente))
                self.conn.commit()
                print(f"O carro {resultado[0]} foi alugado para o cliente: {cliente}.")
            else:
                print(f"O carro: {resultado[0]}, não está mais disponivel para alugar.")
        except sqlite3.Error as e:
            print(f"Erro ao tentar alugar o carro : {e}")

    def lista_carros_disponiveis(self):
        self.c.execute("SELECT id, nome FROM carros WHERE disponivel = 1")
        carros = self.c.fetchall()
        print("\nCarros disponiveis: ")
        for carro in carros:
            print(f"ID: {carro[0]}, Carro: {carro[1]}")
    
    def lista_carros_alugados(self):
        self.c.execute("SELECT carros.nome, carros_alugados.id, carros_alugados.cliente FROM carros_alugados JOIN carros ON carros.id = carros_alugados.carro_id")
        alugados = self.c.fetchall()
        print("\nCarros alugados:")
        for alugado in alugados:
            # print(alugado)
            print(f"Id do aluguel: {alugado[1]}, Carro: {alugado[2]}, Cliente: {alugado[2]}")

    def deletar_carro(self,carro_id):
        if not carro_id:
            print("Erro: Id do carro não pode estar vazio.")
            return
        try:
            self.c.execute("DELETE FROM carros WHERE id = ?", (carro_id))
            self.conn.commit()
            print(f"Carro id: {carro_id} excluido com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao excluir carro id: {carro_id} : {e}")

    def devolver_carro(self, aluguel_id):
        if not aluguel_id:
            print("O id do carro não pode estar vazio.")
            return
        try:
            self.c.execute("SELECT carro_id FROM carros_alugados WHERE id = ?", [aluguel_id])
            resultado = self.c.fetchone()
            if resultado:
                carro_id = resultado[0]
                self.c.execute("SELECT nome FROM carros WHERE id = ?", [carro_id])
                carro_nome = self.c.fetchone()
                self.c.execute("UPDATE carros SET disponivel = 1 WHERE id = ?", [carro_id])
                self.c.execute("DELETE FROM carros_alugados WHERE carro_id = ?", [carro_id])
                self.conn.commit()
                print(f"O carro {carro_nome[0]} foi devolvido!")
            else:
                print(f"O carro {carro_nome[0]} não foi encontrado nos registros de aluguel")
        except sqlite3.Error as e:
            print(f"Erro ao devolver {carro_nome[0]} : {e}")
        
    def fechar_conn(self):
        self.conn.close()

def menu():
    
    print("\n========= MENU =========")
    print("1. Listar carros disponiveis")
    print("2. Listar carros alugados")
    print("3. Alugar carro")
    print("4. Devolver carro") #TODO
    print("5. Adicionar novo carro")
    print("6. Excluir carro")
    print("7. Sair")

if __name__ == "__main__":
    locadora = Locadora("locadora.db")
    os.system("cls")

    while True:
        
        menu()
        opcao = input("\n Escolha uma opção: ")

        if opcao == "1":
            os.system("cls")
            locadora.lista_carros_disponiveis()
        elif opcao == "2":
            os.system("cls")
            locadora.lista_carros_alugados()
        elif opcao == "3":
            os.system("cls")
            cliente = input("Digite seu nome: ")
            carro_id = input("Digite o id do carro desejado: ")
            locadora.aluga_carro(cliente, carro_id)
        elif opcao == "4":
            os.system("cls")
            carro_devolver = input("Qual o id do aluguel que deseja devolver?: ")
            locadora.devolver_carro(carro_devolver)
        elif opcao == "5":
            os.system("cls")
            novo_carro_nome = input("Digite o nome do carro que deseja cadastrar: ")
            novo_carro = Carro(novo_carro_nome)
            locadora.adiciona_carro(novo_carro)
        elif opcao == "6":
            os.system("cls")
            carro_excluir = input("Digite o id do carro que deseja excluir: ")
            locadora.deletar_carro(carro_excluir)
        elif opcao == "7":
            print("\nSaindo...")
            break
        else:
            print("Insira uma opção válida")
    
    locadora.fechar_conn()

