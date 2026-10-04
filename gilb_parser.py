# gilb_parser.py
# Парсер для расчета метрики Джилба по исходному коду на Python.
# Использует ast для разбора и tkinter для GUI.
#
# Правила (итоговые):
#   CL  — количество условных операторов IF-THEN-ELSE (elif — отдельный IF,
#         else — нет) + вклад от match/case (n явных веток → n-1 IF,
#         глубина n-2). case _ игнорируется.
#   CL  — циклы for/while тоже считаются ветвлениями (по заданию).
#   CLI — максимальная глубина вложенности условных операторов.
#   N   — общее количество операторов (statement-узлы AST).
#         pass считается, docstring — нет.
#   cl  — CL / N.

import ast
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


# ---------- Счётчик операторов ----------

class StatementCounter(ast.NodeVisitor):
    """Считает количество операторов (statement nodes) в AST.
    pass считается, docstring — нет."""

    def __init__(self):
        self.count = 0

    def _is_docstring(self, node):
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )

    def generic_visit(self, node):
        if isinstance(node, ast.stmt):
            if self._is_docstring(node):
                pass  # docstring — не оператор
            else:
                self.count += 1  # pass и всё остальное — считаем
        super().generic_visit(node)


# ---------- Счётчик метрики Джилба ----------

class GilbVisitor(ast.NodeVisitor):
    """Считает CL и CLI по правилам Джилба."""

    def __init__(self):
        self.CL = 0
        self.CLI = 0
        self.depth = 0

    def _enter(self, delta):
        self.depth += delta
        if self.depth > self.CLI:
            self.CLI = self.depth

    def _leave(self, delta):
        self.depth -= delta

    def visit_If(self, node):
        # сам if
        self.CL += 1
        self._enter(1)

        # тело if
        for stmt in node.body:
            self.visit(stmt)

        self._leave(1)

        # orelse:
        #   elif  — это ast.If внутри orelse, семантически вложенный if,
        #           поэтому глубину увеличиваем;
        #   else  — просто операторы на той же глубине.
        if node.orelse:
            if isinstance(node.orelse[0], ast.If):
                self._enter(1)
                for stmt in node.orelse:
                    self.visit(stmt)
                self._leave(1)
            else:
                for stmt in node.orelse:
                    self.visit(stmt)

    def visit_For(self, node):
        self.CL += 1
        self._enter(1)
        for stmt in node.body:
            self.visit(stmt)
        self._leave(1)
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_While(self, node):
        self.CL += 1
        self._enter(1)
        for stmt in node.body:
            self.visit(stmt)
        self._leave(1)
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_Match(self, node):
        # Считаем только явные ветки case (не case _).
        explicit_cases = 0
        for case in node.cases:
            if case.pattern is None:
                continue
            # case _ — это MatchAs с pattern=None
            if isinstance(case.pattern, ast.MatchAs) and case.pattern.pattern is None:
                continue
            explicit_cases += 1

        n = explicit_cases
        if n >= 1:
            self.CL += (n - 1)
            delta = max(n - 2, 0)
            self._enter(delta)
            for case in node.cases:
                for stmt in case.body:
                    self.visit(stmt)
            self._leave(delta)
        else:
            for case in node.cases:
                for stmt in case.body:
                    self.visit(stmt)

    def visit_FunctionDef(self, node):
        # Функция не увеличивает CL и CLI, тело обходим
        for stmt in node.body:
            self.visit(stmt)

    def visit_AsyncFunctionDef(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ClassDef(self, node):
        for stmt in node.body:
            self.visit(stmt)


# ---------- Основная логика ----------

def analyze_code(source):
    """Разбирает исходный код и возвращает (CL, N, cl, CLI)."""
    tree = ast.parse(source)

    counter = StatementCounter()
    counter.visit(tree)
    N = counter.count

    gilb = GilbVisitor()
    gilb.visit(tree)
    CL = gilb.CL
    CLI = gilb.CLI

    cl = CL / N if N > 0 else 0.0
    return CL, N, cl, CLI


# ---------- GUI ----------

class ParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер метрики Джилба")
        self.root.geometry("800x600")

        self.btn_open = tk.Button(
            root, text="Загрузить файл с кодом", command=self.load_file
        )
        self.btn_open.pack(pady=5)

        self.text_code = scrolledtext.ScrolledText(root, height=20, width=90)
        self.text_code.pack(pady=5)

        self.btn_analyze = tk.Button(
            root, text="Анализировать", command=self.analyze
        )
        self.btn_analyze.pack(pady=5)

        self.text_result = scrolledtext.ScrolledText(root, height=8, width=90)
        self.text_result.pack(pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return
        self.text_code.delete("1.0", tk.END)
        self.text_code.insert(tk.END, source)

    def analyze(self):
        source = self.text_code.get("1.0", tk.END)
        if not source.strip():
            messagebox.showwarning("Внимание", "Код пуст")
            return
        try:
            CL, N, cl, CLI = analyze_code(source)
        except SyntaxError as e:
            messagebox.showerror("Ошибка синтаксиса", str(e))
            return
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        result = (
            f"Абсолютная сложность (CL): {CL}\n"
            f"Количество операторов (N): {N}\n"
            f"Относительная сложность (cl): {cl:.4f}\n"
            f"Максимальный уровень вложенности (CLI): {CLI}\n"
        )
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, result)


def main():
    root = tk.Tk()
    app = ParserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()