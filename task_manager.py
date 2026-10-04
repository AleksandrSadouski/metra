import sys

TASKS = []
NEXT_ID = 1


def show_menu():
    print("\n=== МЕНЕДЖЕР ЗАДАЧ ===")
    print("1 - Добавить задачу")
    print("2 - Показать все задачи")
    print("3 - Отметить задачу выполненной")
    print("4 - Удалить задачу")
    print("5 - Показать статистику")
    print("0 - Выход")
    print("======================")


def add_task(title, priority):
    global NEXT_ID
    if not title:
        print("Ошибка: пустое название задачи")
        return None
    if priority < 1 or priority > 5:
        print("Ошибка: приоритет должен быть от 1 до 5")
        return None
    task = {"id": NEXT_ID, "title": title, "priority": priority, "done": False}
    TASKS.append(task)
    NEXT_ID += 1
    print(f"Задача #{task['id']} добавлена")
    return task


def list_tasks():
    if not TASKS:
        print("Список задач пуст")
        return
    print("\n--- Список задач ---")
    for task in TASKS:
        if task["done"]:
            status = "выполнена"
        else:
            status = "в работе"
        print(f"#{task['id']} [{status}] {task['title']} (приоритет {task['priority']})")


def mark_done(task_id):
    for task in TASKS:
        if task["id"] == task_id:
            if task["done"]:
                print("Задача уже выполнена")
                return False
            task["done"] = True
            print(f"Задача #{task_id} отмечена выполненной")
            return True
    print(f"Задача #{task_id} не найдена")
    return False


def delete_task(task_id):
    for index, task in enumerate(TASKS):
        if task["id"] == task_id:
            TASKS.pop(index)
            print(f"Задача #{task_id} удалена")
            return True
    print(f"Задача #{task_id} не найдена")
    return False


def show_stats():
    total = len(TASKS)
    done_count = 0
    for task in TASKS:
        if task["done"]:
            done_count += 1
    if total == 0:
        print("Статистика: задач нет")
        return
    percent = done_count * 100 // total
    print(f"Всего задач: {total}")
    print(f"Выполнено: {done_count}")
    print(f"Процент выполнения: {percent}%")


def process_command(command):
    match command:
        case 1:
            title = input("Введите название задачи: ").strip()
            try:
                priority = int(input("Введите приоритет (1-5): "))
            except ValueError:
                print("Ошибка: приоритет должен быть числом")
                return True
            add_task(title, priority)
        case 2:
            list_tasks()
        case 3:
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("Ошибка: ID должен быть числом")
                return True
            mark_done(task_id)
        case 4:
            try:
                task_id = int(input("Введите ID задачи: "))
            except ValueError:
                print("Ошибка: ID должен быть числом")
                return True
            delete_task(task_id)
        case 5:
            show_stats()
        case 0:
            print("Выход из программы")
            return False
        case _:
            print("Неизвестная команда")
    return True


def main():
    print("Добро пожаловать в менеджер задач!")
    running = True
    while running:
        show_menu()
        try:
            command = int(input("Выберите пункт меню: "))
        except ValueError:
            print("Ошибка: введите число")
            continue
        running = process_command(command)
    print("Программа завершена")


if __name__ == "__main__":
    main()