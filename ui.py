import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import json
from account_manager import AccountManager
from story_scheduler import StoryScheduler
from database import Database

class BotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Telegram Story Bot")
        self.root.geometry("800x600")
        
        self.db = Database()
        self.account_manager = AccountManager(self.db)
        self.scheduler = StoryScheduler()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладка аккаунтов
        accounts_frame = ttk.Frame(notebook)
        notebook.add(accounts_frame, text='Аккаунты')
        self.setup_accounts_tab(accounts_frame)
        
        # Вкладка планировщика
        scheduler_frame = ttk.Frame(notebook)
        notebook.add(scheduler_frame, text='Планировщик')
        self.setup_scheduler_tab(scheduler_frame)
        
        # Вкладка статистики
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text='Статистика')
        self.setup_stats_tab(stats_frame)
        
    def setup_accounts_tab(self, parent):
        # Форма добавления аккаунта
        add_frame = ttk.LabelFrame(parent, text="Добавить аккаунт", padding=10)
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="Телефон:").grid(row=0, column=0, sticky='w')
        self.phone_entry = ttk.Entry(add_frame)
        self.phone_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Прокси:").grid(row=1, column=0, sticky='w')
        self.proxy_entry = ttk.Entry(add_frame)
        self.proxy_entry.grid(row=1, column=1, padx=5)
        
        ttk.Button(add_frame, text="Добавить", 
                  command=self.add_account).grid(row=2, column=0, columnspan=2)
        
        # Список аккаунтов
        list_frame = ttk.LabelFrame(parent, text="Аккаунты", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.accounts_tree = ttk.Treeview(list_frame, columns=('phone', 'status'),
                                        show='headings')
        self.accounts_tree.heading('phone', text='Телефон')
        self.accounts_tree.heading('status', text='Статус')
        self.accounts_tree.pack(fill='both', expand=True)
        
    def setup_scheduler_tab(self, parent):
        # Форма планирования
        plan_frame = ttk.LabelFrame(parent, text="Запланировать истории", padding=10)
        plan_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(plan_frame, text="Аккаунт:").grid(row=0, column=0, sticky='w')
        self.account_combo = ttk.Combobox(plan_frame)
        self.account_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(plan_frame, text="Папка с медиа:").grid(row=1, column=0, sticky='w')
        self.media_entry = ttk.Entry(plan_frame)
        self.media_entry.grid(row=1, column=1, padx=5)
        ttk.Button(plan_frame, text="Обзор", 
                  command=self.browse_media).grid(row=1, column=2)
        
        ttk.Label(plan_frame, text="Файл с упоминаниями:").grid(row=2, column=0, sticky='w')
        self.mentions_entry = ttk.Entry(plan_frame)
        self.mentions_entry.grid(row=2, column=1, padx=5)
        ttk.Button(plan_frame, text="Обзор", 
                  command=self.browse_mentions).grid(row=2, column=2)
        
        ttk.Label(plan_frame, text="Ссылка:").grid(row=3, column=0, sticky='w')
        self.link_entry = ttk.Entry(plan_frame)
        self.link_entry.grid(row=3, column=1, padx=5)
        
        ttk.Button(plan_frame, text="Запланировать", 
                  command=self.schedule_stories).grid(row=4, column=0, columnspan=3)
        
        # Список запланированных историй
        queue_frame = ttk.LabelFrame(parent, text="Очередь", padding=10)
        queue_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.queue_tree = ttk.Treeview(queue_frame, 
                                     columns=('account', 'time', 'status'),
                                     show='headings')
        self.queue_tree.heading('account', text='Аккаунт')
        self.queue_tree.heading('time', text='Время')
        self.queue_tree.heading('status', text='Статус')
        self.queue_tree.pack(fill='both', expand=True)
        
    def setup_stats_tab(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Статистика публикаций", padding=10)
        stats_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.stats_tree = ttk.Treeview(stats_frame, 
                                     columns=('date', 'account', 'stories', 'views'),
                                     show='headings')
        self.stats_tree.heading('date', text='Дата')
        self.stats_tree.heading('account', text='Аккаунт')
        self.stats_tree.heading('stories', text='Историй')
        self.stats_tree.heading('views', text='Просмотров')
        self.stats_tree.pack(fill='both', expand=True)
        
    def add_account(self):
        phone = self.phone_entry.get()
        proxy = self.proxy_entry.get()
        
        try:
            self.account_manager.add_account(phone, json.loads(proxy))
            messagebox.showinfo("Успех", "Аккаунт успешно добавлен")
            self.update_accounts_list()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            
    def browse_media(self):
        folder = filedialog.askdirectory()
        if folder:
            self.media_entry.delete(0, tk.END)
            self.media_entry.insert(0, folder)
            
    def browse_mentions(self):
        file = filedialog.askopenfilename()
        if file:
            self.mentions_entry.delete(0, tk.END)
            self.mentions_entry.insert(0, file)
            
    def schedule_stories(self):
        account = self.account_combo.get()
        media_folder = self.media_entry.get()
        mentions_file = self.mentions_entry.get()
        link = self.link_entry.get()
        
        try:
            self.scheduler.schedule_for_account(
                self.db, account, media_folder, mentions_file, link
            )
            messagebox.showinfo("Успех", "Истории запланированы")
            self.update_queue_list()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            
    def update_accounts_list(self):
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
            
        for account in self.db.get_all_accounts():
            self.accounts_tree.insert('', 'end', values=(account[0], 'Активен'))
            
    def update_queue_list(self):
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        for task in self.db.get_pending_stories():
            self.queue_tree.insert('', 'end', 
                                 values=(task[1], task[5], task[6]))
            
    def run(self):
        self.update_accounts_list()
        self.update_queue_list()
        self.root.mainloop()