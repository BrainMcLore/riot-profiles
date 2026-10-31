import queue
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

from . import core, install, windows, i18n

BG = '#101114'
PANEL = '#191b20'
TEXT = '#f1f0ed'
MUTED = '#979ba4'
RED = '#d93643'


class Launcher(tk.Tk):
    def destroy(self):
        # Language changes recreate the root. Cancel timers before removing
        # their Tcl commands so none can fire against the previous window.
        try:
            for timer in self.tk.splitlist(self.tk.call('after', 'info')):
                self.after_cancel(timer)
        except tk.TclError:
            pass
        super().destroy()

    def __init__(self, paths, setup=False, prompt_language=True, selected_profile=None):
        super().__init__()
        self.withdraw()
        self.paths = paths
        self.restart = False
        self.cancelled = False
        self.last_selected = selected_profile
        preferences = i18n.preferences(paths)
        self.t = i18n.Translator(preferences.get('language', 'en'))
        if prompt_language and (preferences.get('show_language_picker', True) or 'language' not in preferences):
            if not self.choose_language():
                self.cancelled = True
                self.destroy()
                return
        self.profiles = core.Profiles(paths)
        self.events = queue.Queue()
        self.busy = False
        self.rows = []
        self.title('Riot Profiles')
        self.geometry('1040x680')
        self.minsize(900, 620)
        self.configure(bg=BG)
        try:
            self.iconbitmap(str(windows.payload() / 'phone.ico'))
        except tk.TclError:
            pass
        top = tk.Frame(self, bg=BG, padx=28, pady=20)
        top.pack(fill='x')
        tk.Label(top, text='RIOT  /  PROFILES', bg=BG, fg=TEXT, font=('Segoe UI', 16, 'bold')).pack(side='left')
        self.button(top, i18n.LANGUAGES[self.t.language] + '  ▾', self.change_language).pack(side='right', padx=(12, 0))
        tk.Label(top, text=self.t('НЕОФИЦИАЛЬНЫЙ ПРОЕКТ  •  v') + core.VERSION, bg=BG, fg=MUTED,
                 font=('Segoe UI', 9)).pack(side='right')
        main = tk.Frame(self, bg=BG)
        main.pack(fill='both', expand=True, padx=24)
        left = tk.Frame(main, bg=PANEL, width=260, padx=16, pady=20)
        left.pack(side='left', fill='y', padx=(0, 16))
        left.pack_propagate(False)
        tk.Label(left, text=self.t('ТВОИ ПРОФИЛИ'), bg=PANEL, fg=MUTED, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        box = tk.Frame(left, bg=PANEL)
        box.pack(fill='both', expand=True, pady=16)
        scroll = tk.Scrollbar(box)
        scroll.pack(side='right', fill='y')
        self.list = tk.Listbox(box, bg=PANEL, fg=TEXT, selectbackground='#343740',
                               selectforeground=TEXT, highlightthickness=0, borderwidth=0,
                               font=('Segoe UI', 12), activestyle='none', exportselection=False,
                               yscrollcommand=scroll.set)
        self.list.pack(fill='both', expand=True)
        scroll.configure(command=self.list.yview)
        self.list.bind('<<ListboxSelect>>', lambda _: self.update_selected())
        self.list.bind('<Double-Button-1>', lambda _: self.launch())
        self.button(left, self.t('+ Добавить профиль'), self.add, RED).pack(fill='x', pady=(8, 8))
        self.button(left, self.t('Переименовать'), self.rename).pack(fill='x', pady=3)
        self.button(left, self.t('Удалить профиль'), self.delete).pack(fill='x', pady=3)
        right = tk.Frame(main, bg=BG)
        right.pack(side='left', fill='both', expand=True)
        self.hero = tk.Canvas(right, bg='#20171d', height=250, highlightthickness=0)
        self.hero.pack(fill='both', expand=True)
        self.hero.bind('<Configure>', self.draw_hero)
        self.name = tk.Label(right, text=self.t('Выбери профиль'), bg=BG, fg=TEXT,
                             font=('Segoe UI', 27, 'bold'), anchor='w', wraplength=640)
        self.name.pack(fill='x', pady=(18, 8))
        tk.Label(right, text=self.t('Отдельные приложения, аккаунты и сохранения для каждого профиля.'),
                 bg=BG, fg=MUTED, font=('Segoe UI', 10), wraplength=600, justify='left').pack(anchor='w')
        actions = tk.Frame(right, bg=BG)
        actions.pack(fill='x', pady=(20, 10))
        self.launch_button = self.button(actions, self.t('▶  ЗАПУСТИТЬ'), self.launch, RED)
        self.launch_button.pack(side='left', ipadx=25, ipady=5)
        self.button(actions, self.t('Открыть Riot Mobile'), lambda: self.launch(riot=True)).pack(side='left', padx=10, ipady=5)
        tools = tk.Frame(right, bg=BG)
        tools.pack(fill='x', pady=(0, 6))
        self.button(tools, self.t('Ярлык профиля'), self.shortcut).pack(side='left')
        self.button(tools, self.t('Холодный запуск'), lambda: self.launch(cold=True)).pack(side='left', padx=8)
        self.button(tools, self.t('Закрыть Android'), self.stop).pack(side='left')
        bottom = tk.Frame(self, bg=BG, padx=28, pady=16)
        bottom.pack(fill='x')
        self.status = tk.StringVar(value=self.t('Android готов.') if core.sdk_ready(paths) else self.t('Первый шаг: установи компоненты Android. Android Studio не нужна.'))
        tk.Label(bottom, textvariable=self.status, bg=BG, fg=MUTED, font=('Segoe UI', 10),
                 wraplength=660, justify='left', anchor='w').pack(side='left', fill='x', expand=True)
        self.setup_button = self.button(bottom, self.t('Установить Android'), self.prepare_setup)
        self.setup_button.pack(side='right')
        self.refresh(selected_profile)
        self.deiconify()
        self.after(100, self.poll)
        if setup:
            self.after(350, self.prepare_setup)

    def choose_language(self):
        dialog = tk.Toplevel(self)
        dialog.title('Riot Profiles · Language')
        dialog.configure(bg=BG)
        w, h = 600, 490
        dialog.geometry(f'{w}x{h}+{max(0, (self.winfo_screenwidth()-w)//2)}+{max(0, (self.winfo_screenheight()-h)//2)}')
        dialog.resizable(False, False)
        frame = tk.Frame(dialog, bg=BG, padx=32, pady=24)
        frame.pack(fill='both', expand=True)
        tk.Label(frame, text='RIOT / PROFILES', bg=BG, fg=TEXT, font=('Segoe UI', 19, 'bold')).pack(anchor='w')
        tk.Label(frame, text='Language / Язык / Мова / Idioma', bg=BG, fg=MUTED,
                 font=('Segoe UI', 12)).pack(anchor='w', pady=(8, 16))
        language = tk.StringVar(value=self.t.language)
        show = tk.BooleanVar(value=i18n.preferences(self.paths).get('show_language_picker', True))
        labels = {
            'ru': ('Показывать выбор языка при запуске', 'Продолжить'),
            'en': ('Show language selection at startup', 'Continue'),
            'uk': ('Показувати вибір мови під час запуску', 'Продовжити'),
            'pt-PT': ('Mostrar a seleção de idioma ao iniciar', 'Continuar'),
        }
        def update_labels():
            check.configure(text=labels[language.get()][0])
            proceed.configure(text=labels[language.get()][1])
        for code, name in i18n.LANGUAGES.items():
            tk.Radiobutton(frame, text=name, value=code, variable=language, command=update_labels,
                           bg=PANEL, fg=TEXT, selectcolor='#3d414c', activebackground='#343740',
                           activeforeground=TEXT, font=('Segoe UI', 12), anchor='w', padx=14, pady=8,
                           indicatoron=False, relief='flat', borderwidth=0).pack(fill='x', pady=3)
        check = tk.Checkbutton(frame, variable=show, bg=BG, fg=TEXT, selectcolor=PANEL,
                               activebackground=BG, activeforeground=TEXT, font=('Segoe UI', 10))
        check.pack(anchor='w', pady=12)
        result = []
        def accept():
            try:
                i18n.save_preferences(self.paths, language.get(), show.get())
            except OSError as error:
                messagebox.showerror('Riot Profiles', str(error), parent=dialog)
                return
            self.t = i18n.Translator(language.get())
            result.append(True)
            dialog.destroy()
        proceed = self.button(frame, '', accept, RED)
        proceed.pack(fill='x', pady=(4, 0))
        update_labels()
        dialog.protocol('WM_DELETE_WINDOW', dialog.destroy)
        dialog.grab_set()
        dialog.lift()
        self.wait_window(dialog)
        return bool(result)

    def change_language(self):
        if self.busy:
            return
        if self.choose_language():
            profile = self.selected(False)
            self.last_selected = profile['id'] if profile else None
            self.restart = True
            self.destroy()

    @staticmethod
    def button(parent, text, command, color='#292c33'):
        return tk.Button(parent, text=text, command=command, bg=color, fg=TEXT,
                         activebackground='#ed4a56' if color == RED else '#3b3f49', activeforeground=TEXT,
                         font=('Segoe UI', 10, 'bold'), relief='flat', borderwidth=0,
                         cursor='hand2', padx=12, pady=10, takefocus=True)

    def draw_hero(self, _=None):
        canvas = self.hero
        canvas.delete('all')
        w, h = canvas.winfo_width(), canvas.winfo_height()
        canvas.create_polygon(w * .60, 0, w, 0, w, h, w * .18, h, fill='#7c2533', outline='')
        canvas.create_polygon(w * .83, 0, w, 0, w, h, w * .42, h, fill='#b62f40', outline='')
        x, y = w * .79, h * .49
        canvas.create_rectangle(x - 35, y - 67, x + 35, y + 67, fill='#17191e', outline='#dfb0b4', width=3)
        canvas.create_rectangle(x - 27, y - 48, x + 27, y + 49, fill=RED, outline='')
        canvas.create_text(x, y, text='RP', fill=TEXT, font=('Segoe UI', 22, 'bold'))
        canvas.create_text(25, 30, text='ANDROID · WINDOWS', fill='#d1b1b8', anchor='nw', font=('Segoe UI', 10, 'bold'))
        canvas.create_text(25, h - 75, text=self.t('ТВОЙ ПРОФИЛЬ.\nТВОЁ ПРОСТРАНСТВО.'), fill=TEXT,
                           anchor='nw', font=('Segoe UI', 20, 'bold'))

    def refresh(self, selected=None):
        old = self.selected(required=False)
        self.rows = self.profiles.load()
        self.list.delete(0, 'end')
        for index, profile in enumerate(self.rows):
            self.list.insert('end', f"  {index + 1:02}   {profile['name']}")
        selected = selected or (old['id'] if old else None)
        index = next((i for i, p in enumerate(self.rows) if p['id'] == selected), 0)
        if self.rows:
            self.list.selection_set(index)
            self.list.see(index)
        self.update_selected()

    def selected(self, required=True):
        indices = self.list.curselection()
        if indices and indices[0] < len(self.rows):
            return dict(self.rows[indices[0]])
        if required:
            messagebox.showinfo(self.t('Профиль'), self.t('Добавь профиль и выбери его в списке.'), parent=self)
        return None

    def update_selected(self):
        profile = self.selected(False)
        self.name.configure(text=profile['name'] if profile else self.t('Добавь первый профиль'))

    def guarded(self, action):
        if self.busy:
            return
        try:
            action()
        except Exception as error:
            messagebox.showerror('Riot Profiles', self.t.message(str(error)), parent=self)

    def add(self):
        if self.busy:
            return
        name = self.ask_name(self.t('Новый профиль'), self.t('Название профиля:'))
        if name is not None:
            self.guarded(lambda: self.refresh(self.profiles.create(name)['id']))

    def rename(self):
        profile = self.selected()
        if profile and not self.busy:
            name = self.ask_name(self.t('Переименовать'), self.t('Новое название:'), profile['name'])
            if name is not None:
                self.guarded(lambda: (self.profiles.rename(profile['id'], name), self.refresh(profile['id'])))

    def ask_name(self, title, prompt, initial=''):
        translate = self.t
        class NameDialog(simpledialog.Dialog):
            def body(dialog, master):
                master.configure(bg=BG)
                dialog.configure(bg=BG)
                tk.Label(master, text=prompt, bg=BG, fg=TEXT, font=('Segoe UI', 11)).pack(anchor='w', padx=14, pady=(14, 8))
                dialog.entry = tk.Entry(master, width=40, font=('Segoe UI', 12), bg=PANEL, fg=TEXT,
                                        insertbackground=TEXT, relief='flat')
                dialog.entry.pack(padx=14, pady=(0, 14), ipady=7)
                dialog.entry.insert(0, initial)
                dialog.entry.select_range(0, 'end')
                return dialog.entry
            def buttonbox(dialog):
                box = tk.Frame(dialog, bg=BG, padx=14, pady=12)
                box.pack(fill='x')
                Launcher.button(box, translate('Сохранить'), dialog.ok, RED).pack(side='right')
                Launcher.button(box, translate('Отмена'), dialog.cancel).pack(side='right', padx=8)
                dialog.bind('<Return>', dialog.ok)
                dialog.bind('<Escape>', dialog.cancel)
            def apply(dialog):
                dialog.result = dialog.entry.get()
        return NameDialog(self, title).result

    def delete(self):
        profile = self.selected()
        if profile and not self.busy and messagebox.askyesno(self.t('Удалить профиль?'),
                self.t('Удалить «{name}» и ВСЕ его приложения, аккаунты и данные?\nЭто действие нельзя отменить.', name=profile['name']),
                icon='warning', parent=self):
            self.work(lambda: (self.profiles.delete(profile['id']), self.events.put(('refresh', None))))

    def work(self, action):
        if self.busy:
            return
        self.busy = True
        self.launch_button.configure(state='disabled')
        self.setup_button.configure(state='disabled')
        def worker():
            try:
                action()
            except Exception as error:
                self.events.put(('error', str(error)))
            finally:
                self.events.put(('done', None))
        threading.Thread(target=worker, daemon=True).start()

    def say(self, text):
        self.events.put(('status', self.t.message(text)))

    def launch(self, cold=False, riot=False):
        profile = self.selected()
        if profile:
            self.status.set(self.t('Запуск: ') + profile['name'])
            def action():
                port, started = core.start_profile(self.paths, profile, cold)
                windows.focus_profile(profile['id'])
                if cold and not started:
                    self.say(self.t('Сначала закрой Android профиля, затем нажми «Холодный запуск».'))
                elif riot:
                    self.say(self.t('Дожидаюсь Android. Первый запуск может занять несколько минут…'))
                    core.open_riot(self.paths, profile, port)
                    self.say(self.t('Открыт Riot Mobile или его страница в Google Play.'))
                else:
                    self.say(self.t('Открыт профиль «{name}». Для переключения выбери другой слева и нажми «Запустить».', name=profile['name']))
            self.work(action)

    def stop(self):
        profile = self.selected()
        if profile:
            self.work(lambda: (core.stop_profile(self.paths, profile), self.say(self.t('Команда закрытия отправлена. Дождись сохранения состояния.'))))

    def shortcut(self):
        profile = self.selected()
        if profile:
            self.guarded(lambda: (windows.create_shortcut(profile=profile), self.status.set(self.t('На рабочем столе создан ярлык прямого запуска этого профиля.'))))

    def prepare_setup(self):
        if self.busy:
            return
        if core.sdk_ready(self.paths):
            self.status.set(self.t('Android уже установлен. Добавь профиль или запусти существующий.'))
            return
        self.status.set(self.t('Получаю список компонентов и лицензии с серверов Google…'))
        self.work(lambda: self.events.put(('plan', install.plan_install())))

    def consent(self, packages):
        dialog = tk.Toplevel(self)
        dialog.title(self.t('Установка Android • лицензии Google'))
        dialog.geometry('760x560')
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text=self.t('Будут скачаны Android Emulator, ADB и Android 13 с Google Play.\n'
                 'Android Studio не устанавливается. Загрузка: около 2 ГБ; нужно 15 ГБ на диске.'),
                 justify='left', padx=18, pady=14).pack(anchor='w')
        box = tk.Frame(dialog)
        box.pack(fill='both', expand=True, padx=18)
        scroll = tk.Scrollbar(box)
        scroll.pack(side='right', fill='y')
        text = tk.Text(box, wrap='word', yscrollcommand=scroll.set)
        text.pack(fill='both', expand=True)
        scroll.configure(command=text.yview)
        text.insert('1.0', '\n\n'.join(p.name + '\n' + p.license for p in packages))
        text.configure(state='disabled')
        accepted = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text=self.t('Я прочитал(а) и принимаю приведённые лицензии Google.'), variable=accepted).pack(anchor='w', padx=18, pady=12)
        def begin():
            if not accepted.get():
                return
            dialog.destroy()
            self.work(lambda: (install.install_sdk(self.paths, packages, True, self.say),
                               self.events.put(('installed', None))))
        tk.Button(dialog, text=self.t('Принять и установить'), command=begin, padx=20, pady=8).pack(pady=(0, 15))

    def poll(self):
        plans = []
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'status':
                    self.status.set(value)
                elif kind == 'done':
                    self.busy = False
                    self.launch_button.configure(state='normal')
                    self.setup_button.configure(state='normal')
                elif kind == 'error':
                    self.status.set(self.t('Операция не завершена. Данные профилей сохранены.'))
                    messagebox.showerror('Riot Profiles', self.t.message(value), parent=self)
                elif kind == 'plan':
                    plans.append(value)
                elif kind == 'installed':
                    self.guarded(windows.install_app)
                    self.status.set(self.t('Готово. Создай профиль и нажми «Запустить».'))
                elif kind == 'refresh':
                    self.refresh()
        except queue.Empty:
            pass
        for packages in plans:
            self.consent(packages)
        self.after(100, self.poll)
