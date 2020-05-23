import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from tkinter import messagebox


class Application(tk.Frame):
    def __init__(self, master: tk.Tk = None):
        super().__init__(master)

        # SQL
        self.db_path = 'todo.sqlite'

        # master
        self.master = master
        self.master_settings()

        # entry button
        self.entry_window = None
        self.entry_title_text = None
        self.entry_content_text = None
        self.create_entry_button()

        # todo list
        self.select_window = None
        self.select_title_text = None
        self.select_content_text = None
        self.tree = None
        self.done_flag = tk.BooleanVar()
        self.all_view_flag = tk.BooleanVar()
        self.create_todo_list()

    def master_settings(self):
        self.master.title('ToDo APP')

    def create_entry_button(self):
        padding = 5

        tk.Button(
            self.master, text='登録画面', command=self.create_entry_window
        ).grid(row=0, column=0, padx=padding, pady=padding, sticky=tk.W+tk.E)

    def create_todo_list(self):
        padding = 5

        self.all_view_flag.set(False)

        tk.Checkbutton(
            self.master, text='すべて表示', var=self.all_view_flag, command=self.get_todo
        ).grid(row=1, padx=padding, pady=padding, sticky=tk.E)

        self.tree = ttk.Treeview(self.master, selectmode='browse')
        self.tree['column'] = (0, 1, 2)
        self.tree['show'] = 'headings'

        self.tree.heading(0, text='タイトル')
        self.tree.heading(1, text='登録日')
        self.tree.heading(2, text='完了日')

        self.tree.column(1, width=150)
        self.tree.column(1, width=150)
        self.tree.column(2, width=150)

        self.tree.bind('<Double-1>', self.create_select_window)

        self.get_todo()

        self.tree.grid(row=2, padx=padding, pady=padding, sticky=tk.W + tk.E)

    def get_todo(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(self.db_path)

        curs = conn.cursor()

        if self.all_view_flag.get():
            sql = '''
                SELECT title, entry_date, done_date FROM todo;
            '''
        else:
            sql = '''
                SELECT title, entry_date, done_date FROM todo WHERE done_date IS NULL;
            '''

        curs.execute(sql)

        for row in curs.fetchall():
            row = list(row)

            if row[2] is None:
                row[2] = ''

            self.tree.insert('', 'end', values=row)

    def create_entry_window(self):
        padding = 5

        self.entry_window = tk.Toplevel(self.master)
        self.entry_window.grab_set()

        tk.Label(self.entry_window, text='タイトル').grid(row=0, padx=padding, pady=padding, sticky=tk.W)
        self.entry_title_text = tk.Text(self.entry_window, width=40, height=1)
        self.entry_title_text.grid(row=1, padx=padding, pady=padding)

        tk.Label(self.entry_window, text='内容').grid(row=2, padx=padding, pady=padding, sticky=tk.W)
        self.entry_content_text = tk.Text(self.entry_window, width=40, height=5)
        self.entry_content_text.grid(row=3, padx=padding, pady=padding)

        tk.Button(
            self.entry_window, text='登録', command=self.entry_todo
        ).grid(row=4, padx=padding, pady=padding, sticky=tk.W + tk.E)

    def entry_todo(self):
        title = self.entry_title_text.get('1.0', 'end').strip()
        content = self.entry_content_text.get('1.0', 'end').strip()

        if self.check_title_content(title, content):
            conn = sqlite3.connect(self.db_path)

            curs = conn.cursor()

            sql = '''
                CREATE TABLE IF NOT EXISTS todo (
                    title TEXT, content TEXT, entry_date TEXT, done_date TEXT
                );
            '''

            curs.execute(sql)

            entry_date = str(datetime.now())

            sql = f'''
                INSERT INTO todo (title, content, entry_date) 
                VALUES ('{title}', '{content}', '{entry_date}');
            '''

            curs.execute(sql)

            conn.commit()

            curs.close()
            conn.close()

            self.get_todo()

            self.entry_window.destroy()
            self.entry_window = None
        else:
            messagebox.showinfo('警告', 'タイトルと内容の両方を入力してください。')

    def create_select_window(self, event):
        padding = 5

        item = self.tree.selection()[0]

        select_data = self.tree.item(item)['values']

        conn = sqlite3.connect(self.db_path)

        curs = conn.cursor()

        sql = f'''
            SELECT * FROM todo WHERE entry_date='{select_data[1]}';
        '''

        curs.execute(sql)

        todo_data = curs.fetchone()

        self.select_window = tk.Toplevel(self.master)
        self.select_window.grab_set()

        tk.Label(self.select_window, text='タイトル').grid(row=0, padx=padding, pady=padding, sticky=tk.W)
        self.select_title_text = tk.Text(self.select_window, width=40, height=1)
        self.select_title_text.insert('1.0', todo_data[0])
        self.select_title_text.grid(row=1, padx=padding, pady=padding)

        tk.Label(self.select_window, text='内容').grid(row=2, padx=padding, pady=padding, sticky=tk.W)
        self.select_content_text = tk.Text(self.select_window, width=40, height=5)
        self.select_content_text.insert('1.0', todo_data[1])
        self.select_content_text.grid(row=3, padx=padding, pady=padding)

        tk.Label(self.select_window, text='登録日').grid(row=4, padx=padding, pady=padding, sticky=tk.W)
        self.select_entry_date_text = tk.Text(self.select_window, width=40, height=1)
        self.select_entry_date_text.insert('1.0', todo_data[2])
        self.select_entry_date_text.configure(state='disable')
        self.select_entry_date_text.grid(row=5, padx=padding, pady=padding)

        if todo_data[3] is None:
            self.done_flag.set(False)
        else:
            self.done_flag.set(True)

        tk.Checkbutton(
            self.select_window, var=self.done_flag, text='完了'
        ).grid(row=6, padx=padding, pady=padding, sticky=tk.E)

        tk.Button(
            self.select_window, text='更新', command=self.update_todo
        ).grid(row=7, padx=padding, pady=padding, sticky=tk.W + tk.E)

        tk.Button(
            self.select_window, text='削除', command=self.delete_todo
        ).grid(row=8, padx=padding, pady=padding, sticky=tk.W + tk.E)

    def update_todo(self):
        title = self.select_title_text.get('1.0', 'end').strip()
        content = self.select_content_text.get('1.0', 'end').strip()
        entry_date = self.select_entry_date_text.get('1.0', 'end').strip()
        done_flag = self.done_flag.get()

        if self.check_title_content(title, content):
            conn = sqlite3.connect(self.db_path)

            curs = conn.cursor()

            if done_flag:
                done_date = str(datetime.now())

                sql = f'''
                    UPDATE todo SET 
                        title='{title}', content='{content}', done_date='{done_date}' 
                    WHERE entry_date='{entry_date}';
                '''
            else:
                sql = f'''
                    UPDATE todo SET title='{title}', content='{content}', done_date=NULL 
                    WHERE entry_date='{entry_date}';
                '''

            curs.execute(sql)

            conn.commit()

            curs.close()
            conn.close()

            self.get_todo()

            self.select_window.destroy()
            self.select_window = None
        else:
            messagebox.showinfo('警告', 'タイトルと内容の両方を入力してください。')

    def delete_todo(self):
        response = messagebox.askyesno('警告', '本当に削除しますか?')

        if response:
            entry_date = self.select_entry_date_text.get('1.0', 'end').strip()

            conn = sqlite3.connect(self.db_path)

            curs = conn.cursor()

            sql = f'''DELETE FROM todo WHERE entry_date='{entry_date}';'''

            curs.execute(sql)

            conn.commit()

            curs.close()
            conn.close()

            self.get_todo()

            self.select_window.destroy()
            self.select_window = None

    @staticmethod
    def check_title_content(title, content):
        if len(title) == 0 or len(content) == 0:
            return False
        else:
            return True


def main():
    master = tk.Tk()

    app = Application(master=master)

    app.mainloop()


if __name__ == '__main__':
    main()
