import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Gastos")
        self.root.geometry("700x500")
        
        self.transactions = []
        self.savings_percentage = tk.DoubleVar(value=10.0)  
        self.reserved_amount = tk.DoubleVar(value=0.0)
        
        self.create_widgets()
        self.graph_canvas = None  
        
        
        self.init_db()
        self.load_transactions()
        self.load_savings_percentage()  
        self.update_summary()  

    def create_widgets(self):
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        
        self.transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_frame, text='Transações')

        
        self.entry_frame = ttk.Frame(self.transactions_frame)
        self.entry_frame.pack(pady=10)
        
        ttk.Label(self.entry_frame, text="Descrição:").grid(row=0, column=0, padx=5, pady=5)
        self.description_entry = ttk.Entry(self.entry_frame)
        self.description_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.entry_frame, text="Valor:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.entry_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.entry_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(self.entry_frame)
        self.category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.entry_frame, text="Adicionar Entrada", command=self.add_income).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.entry_frame, text="Adicionar Saída", command=self.add_expense).grid(row=3, column=1, padx=5, pady=5)
        
        
        self.transactions_tree_frame = ttk.Frame(self.transactions_frame)
        self.transactions_tree_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.transactions_tree_frame, columns=("Descrição", "Valor", "Categoria", "Data"), show='headings')
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Valor", text="Valor")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Data", text="Data")
        self.tree.pack(pady=10)
        
        
        self.summary_frame = ttk.Frame(self.transactions_frame)
        self.summary_frame.pack(pady=10)
        
        self.income_label = ttk.Label(self.summary_frame, text="Total de Entradas: R$0.00")
        self.income_label.pack(pady=5)
        
        self.expense_label = ttk.Label(self.summary_frame, text="Total de Saídas: R$0.00")
        self.expense_label.pack(pady=5)
        
        
        self.savings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.savings_frame, text='Configuração de Economia')

        ttk.Label(self.savings_frame, text="Porcentagem de Economia (%):").grid(row=0, column=0, padx=5, pady=5)
        self.savings_entry = ttk.Entry(self.savings_frame, textvariable=self.savings_percentage)
        self.savings_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.savings_frame, text="Atualizar", command=self.update_savings).grid(row=0, column=2, padx=5, pady=5)
        
        self.reserved_label = ttk.Label(self.savings_frame, text="Valor a Guardar (Reserva): R$0.00")
        self.reserved_label.grid(row=1, column=0, columnspan=3, pady=10)

        
        self.statement_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.statement_frame, text='Extrato')
        
        self.statement_text = tk.Text(self.statement_frame, wrap='word')
        self.statement_text.pack(expand=True, fill='both')
        ttk.Button(self.statement_frame, text="Gerar Extrato", command=self.generate_statement).pack(pady=10)
        
        
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text='Analytics')
        
        ttk.Button(self.analytics_frame, text="Gerar Gráfico", command=self.generate_graph).pack(pady=10)

    def init_db(self):
        
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()
        
       
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            amount REAL,
            category TEXT,
            date TEXT,
            type TEXT
        )
        ''')
        
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT
        )
        ''')
        
        self.conn.commit()

    def add_income(self):
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        
        if not description or not amount or not category:
            messagebox.showwarning("Entrada Inválida", "Por favor, preencha todos os campos.")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Valor Inválido", "Por favor, insira um valor numérico válido.")
            return
        
        
        self.cursor.execute('''
        INSERT INTO transactions (description, amount, category, date, type)
        VALUES (?, ?, ?, ?, ?)
        ''', (description, amount, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Entrada'))
        self.conn.commit()
        
        self.load_transactions()
        self.update_summary()
        self.generate_graph()  
        
    def add_expense(self):
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        
        if not description or not amount or not category:
            messagebox.showwarning("Entrada Inválida", "Por favor, preencha todos os campos.")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Valor Inválido", "Por favor, insira um valor numérico válido.")
            return
        
        
        self.cursor.execute('''
        INSERT INTO transactions (description, amount, category, date, type)
        VALUES (?, ?, ?, ?, ?)
        ''', (description, -amount, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Saída'))
        self.conn.commit()
        
        self.load_transactions()
        self.update_summary()
        self.generate_graph()  
        
    def load_transactions(self):
        self.transactions.clear()
        self.cursor.execute('SELECT description, amount, category, date, type FROM transactions')
        rows = self.cursor.fetchall()
        for row in rows:
            self.transactions.append({
                "Descrição": row[0],
                "Valor": row[1],
                "Categoria": row[2],
                "Data": datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),
                "Tipo": row[4]
            })
        self.update_treeview()
        
    def load_savings_percentage(self):
        self.cursor.execute('SELECT value FROM settings WHERE key = "savings_percentage"')
        row = self.cursor.fetchone()
        if row:
            self.savings_percentage.set(float(row[0]))
        else:
            
            self.savings_percentage.set(10.0)
        
    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for transaction in self.transactions:
            self.tree.insert("", tk.END, values=(transaction["Descrição"], f'R${transaction["Valor"]:.2f}', transaction["Categoria"], transaction["Data"].strftime("%d/%m/%Y %H:%M")))
        
    def update_summary(self):
        total_income = sum(t["Valor"] for t in self.transactions if t["Tipo"] == "Entrada")
        total_expense = -sum(t["Valor"] for t in self.transactions if t["Tipo"] == "Saída")
        balance = total_income - total_expense
        total_savings = balance * (self.savings_percentage.get() / 100)
        
        self.income_label.config(text=f"Total de Entradas: R${total_income:.2f}")
        self.expense_label.config(text=f"Total de Saídas: R${total_expense:.2f}")
        self.reserved_amount.set(total_savings)
        self.reserved_label.config(text=f"Valor a Guardar (Reserva): R${total_savings:.2f}")
        
    def update_savings(self):
        try:
            savings_percentage = float(self.savings_entry.get())
            if savings_percentage < 0 or savings_percentage > 100:
                raise ValueError
            self.savings_percentage.set(savings_percentage)
            
            
            self.cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES ("savings_percentage", ?)
            ''', (savings_percentage,))
            self.conn.commit()
            
            self.update_summary()
        except ValueError:
            messagebox.showwarning("Valor Inválido", "Por favor, insira um valor percentual válido entre 0 e 100.")

    def generate_graph(self):
       
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
        
       
        fig, self.ax = plt.subplots()
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.analytics_frame)
        self.graph_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        total_income = sum(t["Valor"] for t in self.transactions if t["Tipo"] == "Entrada")
        total_expense = -sum(t["Valor"] for t in self.transactions if t["Tipo"] == "Saída")
        balance = total_income - total_expense
        
        
        categories = ['Entrada', 'Saída', 'Saldo']
        values = [total_income, total_expense, balance]
        bar_colors = ['green', 'red', 'blue'] if balance >= 0 else ['green', 'red', 'orange']

        self.ax.clear()  
        self.ax.bar(categories, values, color=bar_colors)
        self.ax.set_ylabel('Valor (R$)')
        self.ax.set_title('Resumo Financeiro')
        self.graph_canvas.draw()
        
    def generate_statement(self):
        self.statement_text.delete(1.0, tk.END)
        for transaction in self.transactions:
            self.statement_text.insert(tk.END, f"Descrição: {transaction['Descrição']}\n")
            self.statement_text.insert(tk.END, f"Valor: R${transaction['Valor']:.2f}\n")
            self.statement_text.insert(tk.END, f"Categoria: {transaction['Categoria']}\n")
            self.statement_text.insert(tk.END, f"Data: {transaction['Data'].strftime('%d/%m/%Y %H:%M')}\n")
            self.statement_text.insert(tk.END, "-"*40 + "\n")
        self.statement_text.insert(tk.END, f"\nTotal de Entradas: R${sum(t['Valor'] for t in self.transactions if t['Tipo'] == 'Entrada'):.2f}\n")
        self.statement_text.insert(tk.END, f"Total de Saídas: R${-sum(t['Valor'] for t in self.transactions if t['Tipo'] == 'Saída'):.2f}\n")
        self.statement_text.insert(tk.END, f"Saldo Final: R${sum(t['Valor'] for t in self.transactions):.2f}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
