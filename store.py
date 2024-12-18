import sqlite3
from hashlib import sha256
import tkinter as tk
from tkinter import messagebox, simpledialog


# Создание базы данных и таблиц
# Создание базы данных и таблиц
def create_database():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    # Таблица пользователей с ролью
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('user', 'admin')) DEFAULT 'user'
        )
    ''')

    # Таблица товаров с новыми характеристиками
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            category TEXT,
            size TEXT,
            energy_class TEXT
        )
    ''')

    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()
    conn.close()



# Хеширование пароля
def hash_password(password):
    return sha256(password.encode()).hexdigest()


# Регистрация нового пользователя
def register(username, password, role='user'):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, hash_password(password), role))
        conn.commit()
        messagebox.showinfo("Регистрация", "Регистрация прошла успешно!")
        print(f"Зарегистрирован пользователь: {username}, Роль: {role}")  # Отладка
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
        print(f"Ошибка регистрации: пользователь {username} уже существует.")  # Отладка

    conn.close()


# Авторизация пользователя
def login(username, password):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    # Проверяем наличие пользователя с указанным именем и хешированным паролем
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                   (username, hash_password(password)))

    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Авторизация", "Авторизация успешна!")
        print(f"Успешная авторизация: {username}, Роль: {user[3]}")  # Отладка
        return user  # Возвращаем всю информацию о пользователе (включая роль)
    else:
        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")
        print(f"Ошибка авторизации: неверные данные для пользователя {username}.")  # Отладка
        return None




# Добавление товара в каталог
def add_product(name, price, category, size, energy_class):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO products (name, price, category, size, energy_class) VALUES (?, ?, ?, ?, ?)',
                   (name, price, category, size, energy_class))
    conn.commit()

    messagebox.showinfo("Успех", f"Товар '{name}' добавлен в каталог.")

    print(
        f"Добавлен товар: {name}, Цена: {price}, Категория: {category}, Размер: {size}, Класс энергопотребления: {energy_class}")  # Отладка

    conn.close()


# Удаление товара из каталога
def remove_product(product_id):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()

    messagebox.showinfo("Успех", f"Товар с ID {product_id} удален из каталога.")

    conn.close()


# Обновление информации о товаре
def update_product(product_id, name, price, category, size, energy_class):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE products
        SET name = ?, price = ?, category = ?, size = ?, energy_class = ?
        WHERE id = ?
    ''', (name, price, category, size, energy_class, product_id))

    conn.commit()
    messagebox.showinfo("Успех", f"Товар с ID {product_id} обновлен.")
    print(
        f"Обновлен товар: ID {product_id}, Название: {name}, Цена: {price}, Категория: {category}, Размер: {size}, Класс энергопотребления: {energy_class}")  # Отладка

    conn.close()


# Просмотр всех товаров
def view_products():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()

    if products:
        product_list = "\n".join(
            [
                f"ID: {product[0]}, Название: {product[1]}, Цена: {product[2]}, Категория: {product[3]}, Размер: {product[4]}, Класс энергопотребления: {product[5]}"
                for product in products])
        messagebox.showinfo("Каталог товаров", product_list)
    else:
        messagebox.showinfo("Каталог товаров", "Каталог пуст.")

    conn.close()

    # Добавление товара в корзину
def add_to_cart(user_id, product_id):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO orders (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()

    messagebox.showinfo("Корзина", "Товар добавлен в корзину.")

    conn.close()

def view_cart(user_id):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute('SELECT products.id, products.name, products.price FROM orders JOIN products ON orders.product_id = products.id WHERE orders.user_id = ?', (user_id,))
    cart_items = cursor.fetchall()

    if cart_items:
        cart_list = "\n".join(
            [f"ID: {item[0]}, Название: {item[1]}, Цена: {item[2]}" for item in cart_items]
        )
        messagebox.showinfo("Корзина", f"Ваши заказы:\n{cart_list}")
    else:
        messagebox.showinfo("Корзина", "Корзина пуста.")

    conn.close()

# Основной класс приложения
class StoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Магазин бытовой техники")
        self.geometry("400x400")

        self.create_widgets()

        create_database()  # Создаем базу данных при запуске приложения

        self.current_user = None  # Сохраняем информацию о текущем пользователе

    def create_widgets(self):
        self.main_frame = tk.Frame(self)
        # Кнопки регистрации и авторизации
        tk.Button(self.main_frame, text="Регистрация", command=self.register_user).pack(pady=10)
        tk.Button(self.main_frame, text="Авторизация", command=self.login_user).pack(pady=10)

        self.product_frame = tk.Frame(self)
        # Кнопка просмотра товаров
        tk.Button(self.product_frame, text="Просмотреть товары", command=view_products).pack(pady=5)

        # Кнопка сортировки товаров по категориям (доступна всем пользователям)
        self.sort_products_button = tk.Button(self.product_frame, text="Сортировать товары по категориям", command=self.sort_products)
        self.sort_products_button.pack(pady=5)

        # Кнопка заказа товара по его ID (доступна всем пользователям)
        self.order_product_button = tk.Button(self.product_frame, text="Заказать товар по ID", command=self.order_product)
        self.order_product_button.pack(pady=5)

        # Кнопка корзины (доступна всем пользователям)
        self.cart_button = tk.Button(self.product_frame, text="Корзина", command=self.view_cart)
        self.cart_button.pack(pady=5)

        # Кнопки добавления и удаления товара будут скрыты для обычных пользователей
        self.add_product_button = tk.Button(self.product_frame, text="Добавить товар", command=self.add_product)
        self.remove_product_button = tk.Button(self.product_frame, text="Удалить товар", command=self.remove_product)

        # Кнопка изменения товара
        self.edit_product_button = tk.Button(self.product_frame, text="Изменить товар", command=self.edit_product)

        # Кнопка выхода из аккаунта
        self.logout_button = tk.Button(self.product_frame, text="Выйти из аккаунта", command=self.logout)

        self.main_frame.pack(pady=20)

    def register_user(self):
        username = simpledialog.askstring("Регистрация", "Введите имя пользователя:")
        password = simpledialog.askstring("Регистрация", "Введите пароль:", show='*')

        if username and password:
            is_admin = messagebox.askyesno("Роль", "Вы хотите зарегистрироваться как администратор?")
            role = 'admin' if is_admin else 'user'
            register(username, password, role)

            print(f"Зарегистрирован пользователь: {username}, Роль: {role}")

    def enable_admin_features(self):
        # Включаем функции для администраторов
        self.add_product_button.pack(pady=5)  # Показываем кнопку добавления товара
        self.remove_product_button.pack(pady=5)  # Показываем кнопку удаления товара
        self.edit_product_button.pack(pady=5)  # Показываем кнопку изменения товара

    def login_user(self):
        username = simpledialog.askstring("Авторизация", "Введите имя пользователя:")
        password = simpledialog.askstring("Авторизация", "Введите пароль:", show='*')

        if username and password:
            user_info = login(username, password)
            if user_info:
                self.current_user = user_info  # Сохраняем информацию о текущем пользователе
                self.switch_to_product_frame()

                # Проверяем роль пользователя для отображения соответствующих функций
                if user_info[3] == 'admin':
                    self.enable_admin_features()  # Включаем функции для администраторов

                else:
                    messagebox.showinfo("Информация",
                                        "Вы вошли как пользователь. У вас нет доступа к добавлению или удалению товаров.")

                print(f"Вошел пользователь: {user_info[1]}, Роль: {user_info[3]}")

    def switch_to_product_frame(self):
        self.main_frame.pack_forget()  # Скрыть главное меню
        self.product_frame.pack(pady=20)  # Показать панель управления товарами
        self.logout_button.pack(pady=10)  # Показать кнопку выхода

    def logout(self):
        self.current_user = None
        self.product_frame.pack_forget()  # Скрыть панель управления товарами
        self.main_frame.pack(pady=20)  # Показать главное меню снова
        self.logout_button.pack_forget()  # Скрыть кнопку выхода

        # Скрываем кнопки добавления и удаления товаров при выходе из аккаунта
        self.add_product_button.pack_forget()
        self.remove_product_button.pack_forget()

    def add_product(self):
        if not self.current_user or self.current_user[3] != 'admin':
            messagebox.showerror("Ошибка доступа", "Только администраторы могут добавлять товары.")
            return

        name = simpledialog.askstring("Добавление товара", "Введите название товара:")

        price_str = simpledialog.askstring("Добавление товара", "Введите цену товара:")

        category = simpledialog.askstring("Добавление товара", "Введите категорию товара:")

        size = simpledialog.askstring("Добавление товара", "Введите размер товара:")

        energy_class = simpledialog.askstring("Добавление товара", "Введите класс энергопотребления:")

        if name and price_str and category and size and energy_class:
            try:
                price = float(price_str)
                add_product(name, price, category, size, energy_class)
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом.")

    def remove_product(self):
        if not self.current_user or self.current_user[3] != 'admin':
            messagebox.showerror("Ошибка доступа", "Только администраторы могут удалять товары.")
            return

        product_id_str = simpledialog.askstring("Удаление товара", "Введите ID товара для удаления:")

        if product_id_str:
            try:
                product_id = int(product_id_str)
                remove_product(product_id)
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть целым числом.")

    def edit_product(self):
        if not self.current_user or self.current_user[3] != 'admin':
            messagebox.showerror("Ошибка доступа", "Только администраторы могут изменять товары.")
            return

        product_id_str = simpledialog.askstring("Редактирование товара", "Введите ID товара для редактирования:")

        if product_id_str:
            try:
                product_id = int(product_id_str)

                # Запрашиваем новую информацию о товаре
                name = simpledialog.askstring("Редактирование товара", "Введите новое название товара:")
                price_str = simpledialog.askstring("Редактирование товара", "Введите новую цену товара:")
                category = simpledialog.askstring("Редактирование товара", "Введите новую категорию товара:")
                size = simpledialog.askstring("Редактирование товара", "Введите новый размер товара:")
                energy_class = simpledialog.askstring("Редактирование товара", "Введите новый класс энергопотребления:")

                if name and price_str and category and size and energy_class:
                    try:
                        price = float(price_str)
                        update_product(product_id, name, price, category, size, energy_class)
                    except ValueError:
                        messagebox.showerror("Ошибка", "Цена должна быть числом.")
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть целым числом.")

    def sort_products(self):
        category = simpledialog.askstring("Сортировка", "Введите категорию для сортировки:")

        if category:
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
            products = cursor.fetchall()

            if products:
                product_list = "\n".join(
                    [
                        f"ID: {product[0]}, Название: {product[1]}, Цена: {product[2]}, Категория: {product[3]}, Размер: {product[4]}, Класс энергопотребления: {product[5]}"
                        for product in products])
                messagebox.showinfo("Товары в категории", product_list)
            else:
                messagebox.showinfo("Товары в категории", "Нет товаров в указанной категории.")

            conn.close()

    def order_product(self):
        product_id_str = simpledialog.askstring("Заказ товара", "Введите ID товара для заказа:")

        if product_id_str:
            try:
                product_id = int(product_id_str)
                if not self.current_user:
                    messagebox.showerror("Ошибка", "Сначала войдите в систему.")
                    return

                user_id = self.current_user[0]  # Получаем ID текущего пользователя

                # Проверяем наличие товара с указанным ID
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()

                if product:
                    add_to_cart(user_id, product_id)  # Добавляем товар в корзину
                    print(f"Заказан товар: {product[1]}, ID: {product_id}")  # Отладка
                else:
                    messagebox.showerror("Ошибка", "Товар с таким ID не найден.")
                    print(f"Ошибка: Товар с ID {product_id} не найден.")  # Отладка

                conn.close()
            except ValueError:
                messagebox.showerror("Ошибка", "ID должен быть целым числом.")

    def view_cart(self):
        if not self.current_user:
            messagebox.showerror("Ошибка", "Сначала войдите в систему.")
            return

        user_id = self.current_user[0]  # Получаем ID текущего пользователя
        view_cart(user_id)  # Вызываем функцию для просмотра содержимого корзины

if __name__ == "__main__":
    app = StoreApp()
    app.mainloop()

