import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import csv
import requests
import urllib3

__version__ = "1.0.0"

# Opcional: Suprimir avisos de HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URLs para os arquivos no GitHub (raw)
url_versao_remota = "https://raw.githubusercontent.com/BrunoMediador/MyProjects/refs/heads/main/versaoPainelRH.text"
url_codigo_atualizado = "https://raw.githubusercontent.com/BrunoMediador/MyProjects/refs/heads/main/PainelRH.py"

def verificar_atualizacao():
    """
    Verifica se há uma nova versão disponível.
    """
    try:
        resposta = requests.get(url_versao_remota, verify=False)
        if resposta.status_code == 200:
            print("Conexão bem-sucedida!")
            versao_remota = resposta.text.strip()  # Remove espaços ou quebras de linha
            print(f"Versão remota: {versao_remota}")

            if versao_remota > __version__:
                print("Há uma nova versão disponível! Atualizando...")
                baixar_nova_versao()
            else:
                print("Você já está usando a versão mais recente.")
        else:
            print(f"Erro ao acessar a URL de versão remota: {resposta.status_code}")
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")


def baixar_nova_versao():
    """
    Baixa a nova versão do código e substitui o arquivo atual.
    """
    try:
        resposta = requests.get(url_codigo_atualizado, verify=False)
        if resposta.status_code == 200:
            with open("teste.py", "w") as arquivo:
                arquivo.write(resposta.text)
            print("Atualização concluída! Reinicie o programa para aplicar as mudanças.")
        else:
            print(f"Erro ao baixar nova versão: {resposta.status_code}")
    except Exception as e:
        print(f"Erro ao atualizar: {e}")


if __name__ == "__main__":
    verificar_atualizacao()


# Paleta de cores suaves e amigáveis
COR_FUNDO = "#F0F8FF"   # Alice Blue
COR_BOTAO = "#00BFFF"   # Deep Sky Blue
COR_BOTAO_HOVER = "#40E0D0"   # Turquoise
COR_ERRO = "#FF6347"   # Tomato
COR_SUCESSO = "#228B22"   # Forest Green
COR_TEXTO = "#212121"   # Dark Gray
COR_LABEL = "#757575"   # Gray
COR_TREEVIEW_CABECALHO = "#B0E0E6"   # Powder Blue


class App:
    def __init__(self):
        self.root = None
        self.login_window = None
        self.current_user = None
        self.selected_id = None
        self.project_ids = {}

        self.setup_login_window()

    def connect_db(self):
        """Conecta ao banco de dados PostgreSQL."""
        return psycopg2.connect(
             host='',
            database='',
            user='',
            password=''
        )

    def fetch_data(self):
        """Busca dados do banco de dados com base nos filtros aplicados."""
        email_filter = self.entry_email_filter.get().strip()
        start_date_filter = self.date_start_filter.get_date().strftime(
            '%Y-%m-%d') if self.date_start_filter.get_date() else None
        end_date_filter = self.date_end_filter.get_date().strftime(
            '%Y-%m-%d') if self.date_end_filter.get_date() else None
        project_filter = self.project_combobox_filter.get()
        type_filter = self.type_combobox_filter.get()

        query = sql.SQL("""
            SELECT id, str_email, str_data, str_project_name, tipo, str_horas, comentario, "item/str_projeto_id", "item/datainsercao", user_insert
            FROM public."Aponta_pingo"
            WHERE (%s IS NULL OR str_email ILIKE %s)
            AND (%s IS NULL OR str_data >= %s)
            AND (%s IS NULL OR str_data <= %s)
            AND (%s IS NULL OR str_project_name = %s)
            AND (%s IS NULL OR tipo = %s);
        """)

        params = (
            None if email_filter == "" else email_filter,
            f"%{email_filter}%",
            start_date_filter,
            start_date_filter,
            end_date_filter,
            end_date_filter,
            None if project_filter == "" else project_filter,
            None if project_filter == "" else project_filter,
            None if type_filter == "" else type_filter,
            None if type_filter == "" else type_filter
        )

        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados: {e}")
            return []

    def insert_data(self, data):
        """Insere um novo registro no banco de dados."""
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    query = sql.SQL("""
                        INSERT INTO public."Aponta_pingo" (
                            str_email, str_data, tipo, str_horas, comentario, "item/str_projeto_id", 
                            str_project_name, "item/datainsercao", user_insert
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """)
                    cursor.execute(query, data)
                    conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inserir dados: {e}")

    def update_data(self, data, id):
        """Atualiza um registro existente no banco de dados."""
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    query = sql.SQL("""
                        UPDATE public."Aponta_pingo"
                        SET str_email = %s, str_data = %s, tipo = %s, str_horas = %s, comentario = %s, 
                        "item/str_projeto_id" = %s, str_project_name = %s, "item/datainsercao" = %s, 
                        user_insert = %s
                        WHERE id = %s;
                    """)
                    cursor.execute(query, (*data, id))
                    conn.commit()
                    messagebox.showinfo(
                        "Sucesso", "Dados atualizados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados: {e}")

    def delete_data(self, ids):
        """Exclui um ou mais registros do banco de dados."""
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    ids_str = ','.join(str(id) for id in ids)
                    query = sql.SQL(
                        f"""
                        UPDATE public."Aponta_pingo" 
                        SET tipo = 'DELETADO', 
                            user_insert = %s 
                        WHERE id IN ({ids_str});
                        """
                    )
                    cursor.execute(query, (self.current_user,))  # Adiciona o usuário logado
                    conn.commit()
                    messagebox.showinfo(
                        "Sucesso", "Dados excluídos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir dados: {e}")

    def fetch_projects(self):
        """Busca a lista de projetos do banco de dados."""
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    query = sql.SQL("""
                        SELECT project_id, nome_projeto
                        FROM public."projects";
                    """)
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar projetos: {e}")
            return []

    def get_project_id(self, project_name):
        """Retorna o ID do projeto com base no nome."""
        return self.project_ids.get(project_name)

    def validate_hours(self, hours):
        """Valida se o valor de horas é um número inteiro."""
        return hours.isdigit()

    def get_current_datetime(self):
        """Retorna a data e hora atuais formatadas."""
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    def load_data(self):
        """Carrega os dados na Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.fetch_data():
            self.tree.insert("", tk.END, values=row)

    def load_projects(self):
        """Carrega a lista de projetos no ComboBox."""
        projects = self.fetch_projects()
        self.project_ids = {project[1]: project[0] for project in projects}
        project_names = list(self.project_ids.keys())
        self.project_combobox['values'] = project_names
        self.project_combobox_filter['values'] = project_names
        if project_names:
            self.project_combobox.set(project_names[0])
            self.project_combobox_filter.set('')

    def insert(self):
        """Insere um novo registro com validação de dados."""
        if any(entry.get() == "" for entry in [self.entry_str_email, self.entry_str_horas, self.entry_comentario]):
            messagebox.showwarning(
                "Erro de Entrada", "Por favor, preencha todos os campos.")
            return

        horas = self.entry_str_horas.get()
        if not self.validate_hours(horas):
            messagebox.showwarning(
                "Erro de Entrada", "Horas devem ser um número inteiro.")
            return

        project_name = self.project_combobox.get()
        project_id = self.get_project_id(project_name)
        if not project_id:
            messagebox.showwarning(
                "Erro de Entrada", "Projeto não encontrado.")
            return

        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        if start_date > end_date:
            messagebox.showwarning(
                "Erro de Entrada", "A data de início não pode ser posterior à data de término.")
            return

        confirm = messagebox.askyesno(
            "Confirmar",
            f"Deseja inserir dados de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}?"
        )

        if confirm:
            self.disable_buttons()
            self.show_wait_message()

            try:
                while start_date <= end_date:
                    date_str = start_date.strftime('%Y-%m-%d')
                    data = (
                        self.entry_str_email.get(),
                        date_str,
                        self.type_combobox.get(),
                        horas,
                        self.entry_comentario.get(),
                        project_id,
                        project_name,
                        self.get_current_datetime(),
                        self.current_user  # Adiciona o usuário logado
                    )
                    self.insert_data(data)
                    start_date += timedelta(days=1)
                messagebox.showinfo(
                    "Sucesso", "Todos os registros foram inseridos.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao inserir dados: {e}")
            finally:
                self.clear_entries()
                self.load_data()
                self.enable_buttons()
                self.hide_wait_message()

    def update(self):
        """Atualiza um registro existente com validação de dados."""
        id = self.selected_id
        if id is None or any(entry.get() == "" for entry in [self.entry_str_email, self.entry_str_horas, self.entry_comentario]):
            messagebox.showwarning(
                "Erro de Entrada", "Por favor, selecione uma linha e preencha todos os campos.")
            return

        horas = self.entry_str_horas.get()
        if not self.validate_hours(horas):
            messagebox.showwarning(
                "Erro de Entrada", "Horas devem ser um número inteiro.")
            return

        date = self.start_date_entry.get_date().strftime('%Y-%m-%d')

        project_name = self.project_combobox.get()
        project_id = self.get_project_id(project_name)
        if not project_id:
            messagebox.showwarning(
                "Erro de Entrada", "Projeto não encontrado.")
            return

        data = (
            self.entry_str_email.get(),
            date,
            self.type_combobox.get(),
            horas,
            self.entry_comentario.get(),
            project_id,
            project_name,
            self.get_current_datetime(),
            self.current_user  # Adiciona o usuário logado
        )
        self.update_data(data, id)
        self.load_data()

    def delete(self):
        """Exclui os registros selecionados após confirmação."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Seleção", "Por favor, selecione uma ou mais linhas para excluir.")
            return

        ids = [self.tree.item(item, "values")[0]
                for item in selected_items]
        confirm = messagebox.askyesno(
            "Confirmar", "Tem certeza de que deseja excluir os registros selecionados?")
        if confirm:
            self.delete_data(ids)
            self.load_data()

    def clear_entries(self):
        """Limpa os campos de entrada."""
        self.entry_str_email.delete(0, tk.END)
        self.start_date_entry.set_date(datetime.today())
        self.end_date_entry.set_date(datetime.today())
        self.entry_str_horas.delete(0, tk.END)
        self.entry_comentario.delete(0, tk.END)
        self.project_combobox.set('')
        self.type_combobox.set('')

    def select_item(self, event):
        """Carrega os dados da linha selecionada nos campos de entrada."""
        item = self.tree.selection()
        if item:
            self.selected_id = self.tree.item(item, "values")[0]
            self.entry_str_email.delete(0, tk.END)
            self.entry_str_email.insert(
                0, self.tree.item(item, "values")[1])
            self.start_date_entry.set_date(datetime.strptime(
                self.tree.item(item, "values")[2], '%Y-%m-%d'))
            self.end_date_entry.set_date(datetime.strptime(
                self.tree.item(item, "values")[2], '%Y-%m-%d'))
            self.entry_str_horas.delete(0, tk.END)
            self.entry_str_horas.insert(
                0, self.tree.item(item, "values")[5])
            self.entry_comentario.delete(0, tk.END)
            self.entry_comentario.insert(
                0, self.tree.item(item, "values")[6])
            self.project_combobox.set(self.tree.item(item, "values")[3])
            self.type_combobox.set(self.tree.item(item, "values")[4])

    def export_data(self):
        """Exporta os dados da Treeview para um arquivo CSV."""
        try:
            with open('dados_apontamento.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Escreve o cabeçalho
                writer.writerow(
                    [self.tree.heading(col, option="text") for col in self.tree['columns']])
                # Escreve os dados
                for row in self.tree.get_children():
                    writer.writerow(self.tree.item(row, "values"))
            messagebox.showinfo(
                "Sucesso", "Dados exportados para 'dados_apontamento.csv' com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {e}")

    def setup_main_window(self):
        """Configura a janela principal da aplicação."""
        self.root = tk.Tk()
        self.root.title("Sistema de Apontamento de Horas")
        self.root.configure(bg=COR_FUNDO)

        # Estilo visual
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=(
            "Helvetica", 10, "bold"), background=COR_TREEVIEW_CABECALHO)
        style.configure("Treeview", font=(
            "Helvetica", 9), background=COR_FUNDO)
        style.configure("TButton", font=(
            "Helvetica", 10), background=COR_BOTAO, foreground="white")
        style.configure("TLabel", font=(
            "Helvetica", 10), background=COR_FUNDO, foreground=COR_LABEL)
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("TCombobox", font=("Helvetica", 10))

        # Configurar cores e estilos dos botões ao passar o mouse
        style.map("TButton",
                  background=[('active', COR_BOTAO_HOVER),
                              ('!disabled', COR_BOTAO)],
                  foreground=[('!disabled', 'white')]
                  )

        # Ajustar o tamanho da janela para o tamanho da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Define o tamanho inicial da janela como 80% da tela
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        # Centraliza a janela
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Painel principal com layout de grid
        main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Filtros
        filter_frame = tk.LabelFrame(
            main_frame, text="Filtros", relief=tk.GROOVE, borderwidth=2, bg=COR_FUNDO)
        filter_frame.grid(row=0, column=0, columnspan=2,
                          sticky="nsew", padx=10, pady=10)

        tk.Label(filter_frame, text="Filtrar por E-mail:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_email_filter = tk.Entry(filter_frame)
        self.entry_email_filter.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(filter_frame, text="Data de Início:",
                 bg=COR_FUNDO, foreground=COR_TEXTO).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.date_start_filter = DateEntry(
            filter_frame, date_pattern='yyyy-mm-dd')
        self.date_start_filter.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(filter_frame, text="Data de Término:",
                 bg=COR_FUNDO, foreground=COR_TEXTO).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_end_filter = DateEntry(
            filter_frame, date_pattern='yyyy-mm-dd')
        self.date_end_filter.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(filter_frame, text="Projeto:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.project_combobox_filter = ttk.Combobox(filter_frame)
        self.project_combobox_filter.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(filter_frame, text="Tipo:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.type_combobox_filter = ttk.Combobox(
            filter_frame, values=["Adicional de produção", "Normal", "DELETADO", "Pendente"])
        self.type_combobox_filter.grid(row=4, column=1, padx=10, pady=5)

        # Botões de filtro lado a lado
        filter_button_frame = tk.Frame(filter_frame, bg=COR_FUNDO)
        filter_button_frame.grid(
            row=5, column=0, columnspan=2, pady=10)

        tk.Button(filter_button_frame, text="Aplicar Filtros",
                  command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(filter_button_frame, text="Limpar Filtros",
                  command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Campos de Inserção/Atualização/Exclusão
        action_frame = tk.LabelFrame(
            main_frame, text="Ações", relief=tk.GROOVE, borderwidth=2, bg=COR_FUNDO)
        action_frame.grid(row=1, column=0, columnspan=2,
                          sticky="nsew", padx=10, pady=10)

        tk.Label(action_frame, text="Email:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_str_email = tk.Entry(action_frame)
        self.entry_str_email.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Data de Início:",
                 bg=COR_FUNDO, foreground=COR_TEXTO).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.start_date_entry = DateEntry(
            action_frame, date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Data de Término:",
                 bg=COR_FUNDO, foreground=COR_TEXTO).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.end_date_entry = DateEntry(
            action_frame, date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Minutos:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_str_horas = tk.Entry(action_frame)
        self.entry_str_horas.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Comentário:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.entry_comentario = tk.Entry(action_frame)
        self.entry_comentario.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Tipo:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.type_combobox = ttk.Combobox(
            action_frame, values=["Adicional de produção", "Normal", "Pendente"])
        self.type_combobox.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(action_frame, text="Projeto:", bg=COR_FUNDO,
                 foreground=COR_TEXTO).grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.project_combobox = ttk.Combobox(action_frame)
        self.project_combobox.grid(row=6, column=1, padx=10, pady=5)

        # Botões
        button_frame = tk.Frame(action_frame, bg=COR_FUNDO)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 10))

        self.button_insert = tk.Button(
            button_frame, text="Inserir", command=self.insert, width=10)
        self.button_insert.pack(side=tk.LEFT, padx=5)
        self.button_update = tk.Button(
            button_frame, text="Atualizar", command=self.update, width=10)
        self.button_update.pack(side=tk.LEFT, padx=5)
        self.button_delete = tk.Button(
            button_frame, text="Excluir", command=self.delete, width=10)
        self.button_delete.pack(side=tk.LEFT, padx=5)

        # Tabela
        tree_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        tree_frame.grid(row=0, column=2, rowspan=2,
                        sticky="nsew", padx=(10, 0))

        self.tree = ttk.Treeview(tree_frame, columns=(
            "id", "str_email", "str_data", "str_project_name", "tipo", "str_horas",
            "comentario", "item/str_projeto_id", "item/datainsercao", "user_insert"
        ), show='headings')

        self.tree.heading("id", text="ID")
        self.tree.heading("str_email", text="Email")
        self.tree.heading("str_data", text="Data")
        self.tree.heading("str_project_name", text="Projeto")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("str_horas", text="Horas")
        self.tree.heading("comentario", text="Comentário")
        self.tree.heading("item/str_projeto_id", text="ID do Projeto")
        self.tree.heading("item/datainsercao", text="Data de Inserção")
        self.tree.heading("user_insert", text="Usuário")

        # Ajusta as colunas para ocupar o espaço disponível
        for col in self.tree['columns']:
            self.tree.column(col, width=100, stretch=tk.YES)

        # Cria um Scrollbar vertical
        vsb = tk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Cria um Scrollbar horizontal
        hsb = tk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Conecta os scrollbars à Treeview
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        # Botão para exportar dados
        export_button = tk.Button(
            main_frame, text="Exportar Dados", command=self.export_data)
        export_button.grid(row=2, column=2, pady=10)

        # Mensagem de espera
        self.wait_message = tk.Label(
            self.root, text="", font=("Helvetica", 14), bg=COR_FUNDO, foreground=COR_TEXTO)
        self.wait_message.grid(row=3, column=0, columnspan=3, pady=20)

        self.load_projects()
        self.load_data()

        # Configurar o grid para redimensionar os elementos
        main_frame.grid_rowconfigure(0, weight=1)  # A linha 0 se expande verticalmente
        # A coluna 2 se expande horizontalmente
        main_frame.grid_columnconfigure(2, weight=1)

        self.root.mainloop()

    def disable_buttons(self):
        """Desabilita os botões."""
        self.button_insert.config(state="disabled")
        self.button_update.config(state="disabled")
        self.button_delete.config(state="disabled")

    def enable_buttons(self):
        """Habilita os botões."""
        self.button_insert.config(state="normal")
        self.button_update.config(state="normal")
        self.button_delete.config(state="normal")

    def show_wait_message(self):
        """Mostra a mensagem de espera."""
        self.wait_message.config(
            text="Aguarde, estamos processando os dados...")
        self.wait_message.update_idletasks()

    def hide_wait_message(self):
        """Esconde a mensagem de espera."""
        self.wait_message.config(text="")
        self.wait_message.update_idletasks()

    def setup_login_window(self):
        """Configura a janela de login."""
        self.login_window = tk.Tk()
        self.login_window.title("Login")

        # Centraliza a janela de login
        self.login_window.update_idletasks()
        window_width = self.login_window.winfo_width()
        window_height = self.login_window.winfo_height()
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.login_window.geometry(f"+{x}+{y}")

        tk.Label(self.login_window, text="Usuário:").grid(
            row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.login_window, text="Senha:").grid(
            row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.login_window, text="Entrar",
                  command=self.login).grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.login_window.mainloop()

    def login(self):
        """Realiza a autenticação do usuário."""
        username = self.username_entry.get().strip().lower()
        password = self.password_entry.get().strip()

        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    query = sql.SQL(
                        "SELECT * FROM public.users_apontamento WHERE users = %s AND password = %s;")
                    cursor.execute(query, (username, password))
                    if cursor.fetchone():
                        self.current_user = username
                        self.login_window.destroy()
                        self.setup_main_window()
                    else:
                        messagebox.showerror(
                            "Erro", "Usuário ou senha incorretos.")
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Erro ao verificar credenciais: {e}")

    def clear_filters(self):
        """Limpa os campos de filtro e recarrega os dados."""
        self.entry_email_filter.delete(0, tk.END)
        self.date_start_filter.set_date(datetime.today())
        self.date_end_filter.set_date(datetime.today())
        self.project_combobox_filter.set('')
        self.type_combobox_filter.set('')
        self.load_data()


if __name__ == "__main__":
    app = App()
