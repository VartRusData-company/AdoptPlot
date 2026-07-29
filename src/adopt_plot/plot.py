
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 VartRusData. All rights reserved.
from sympy import *
import numpy as np
import matplotlib.pyplot as plt
import logging
import re
import sympy


from . import TooManyVariablesError, PltNotFoundError

def get_all_sympy_function_names():
    """Собирает имена всех встроенных функций и констант SymPy."""
    names = set(sympy.__all__)
    #print(names)
    return names


def insert_multiplication_signs(expr: str, extra_functions=None) -> str:
    """
    Вставляет знаки умножения с учётом неявного умножения.
    Поддерживает латиницу и кириллицу в именах переменных.
    Защищает все известные SymPy-функции и константы от разбиения.
    """
    func_set = get_all_sympy_function_names()  # теперь там и функции, и константы
    if extra_functions:
        func_set.update(extra_functions)

    sorted_funcs = sorted(func_set, key=len, reverse=True)
    func_pattern = '|'.join(re.escape(f) for f in sorted_funcs)

    LETTER = r'[A-Za-zА-Яа-яёЁ_]'
    LETTER_DIGIT = r'[\dA-Za-zА-Яа-яёЁ_]'

    # === ШАГ 1: Защита известных имён (функций и констант) ===
    protected = {}

    def protect_known(match):
        name = match.group(0)
        if name not in func_set:
            return name
        placeholder = f'\ue000{len(protected)}\ue001'
        protected[placeholder] = name
        return placeholder

    #print(expr)
    expr = re.sub(r'[A-Za-z_]\w*', protect_known, expr)
    #print(expr)
    # === ШАГ 2: Правила вставки умножения ===
    expr = re.sub(rf'(\d+)(\ue000\d+\ue001)(?=\()', r'\1*\2', expr)
    # Явно вставляем * между цифрой/буквой и известным именем перед '('
    expr = re.sub(rf'(\d)({func_pattern})(?=\()', r'\1*\2', expr)
    expr = re.sub(rf'({LETTER})({func_pattern})(?=\()', r'\1*\2', expr)

    # Основные правила с кириллицей
    expr = re.sub(rf'(\d)({LETTER})', r'\1*\2', expr)  # 2x, 2я
    # РАЗРЫВАЕМ ВСЕ ЦЕПОЧКИ БУКВ (кроме защищённых имён)
    expr = re.sub(rf'({LETTER})(?={LETTER})', r'\1*', expr)  # a*b*c, а*я
    expr = re.sub(rf'({LETTER_DIGIT})(\()', r'\1*\2', expr)  # a(, 3(, я(
    expr = re.sub(rf'(\))({LETTER_DIGIT}\()', r'\1*\2', expr)  # )a, )(, )я

    # === ШАГ 3: Возвращаем защищённые имена на место ===
    for placeholder, name in protected.items():
        expr = expr.replace(placeholder, name)

    return expr







from typing import Literal, Optional, Tuple

class AdoptPlot:
    def __init__(self,
               expr: str,
               lib: Literal['contour', 'implicit', None] = None,
               xlims: Tuple[float, float] = (-20, 20),
               ylims: Tuple[float, float] = (-20, 20),
               n: int = 10000,

               depth: int = 9,
               linewidth: float = 2.0,
               limit: float | Tuple[float, float, float, float] = 100,
               color: str = 'blue',
               legend: bool = True,
               points: bool = True,
               grid: bool = True,
               interact: bool = True,
               show: bool = True,
               text_legend: Optional[str] = None
               ):
        """
        Plots an implicit function with adaptive engine selection.

        Parameters:
            expr: String containing the equation (e.g., "y = 1/x").
            lib: Forced plotting engine ('contour', 'implicit', or None for auto-selection).
            xlims :Initial visible range for the plot.
            ylims: Initial visible range for the plot.
            n: Grid density for the contour engine.
            depth: Adaptive refinement depth for plot_implicit.
            linewidth: Thickness of the plot line.
            limit: Defines the computational domain for the plot. Accepts a single number (for a square area) or a tuple of 4 floats (x_min, x_max, y_min, y_max) for a rectangular area.
            color: Line color.
            legend: Whether to display the legend.
            points: Whether to display axis intersection points.
            grid: Whether to display the grid.
            interact: Allow zooming/panning (does not fix limits rigidly).
            show: If False, returns a PlotHandle object instead of displaying the plot.
            text_legend: Additional text for the legend (supports "\\n" and a list of strings).
    """
        try:
            self.lib = lib
            self.xlims = xlims
            self.ylims = ylims
            self.n = n
            self.depth = depth
            self.linewidth = linewidth
            self.color = color
            self.legend = legend
            self.points = points
            self.grid = grid
            self.interact = interact
            self.is_show = show
            self.limit = limit
            self.text_legend = text_legend
            # Получаем уравнения из поля ввода
            equations_str = expr
            logging.info(f"Полученная строка уравнений: {equations_str}")
            if equations_str == "":
                raise ValueError("Empty string is not allowed.")
            # Проверяем наличие запятых в строке
            equation = equations_str
            # Разбиение строки на отдельные уравнения



            # Преобразование уравнений в объекты Sympy
            expressions = []
            used_variables = set()  # Множество переменных, используемых в уравнениях

            logging.info(f"Преобразование уравнения: {equation}")

            equation = insert_multiplication_signs(equation)

            lhs, rhs = equation.split('=')
            logging.info(str(lhs))
            logging.info(str(rhs))
            expressions.append(Eq(sympify(lhs), sympify(rhs)))
            logging.info(f"Добавлено уравнение: {expressions[-1]}")

            # Определяем переменные, участвующие в текущем уравнении
            used_variables.update(list(expressions[-1].free_symbols))

            logging.info(f"Переменные, задействованные в уравнениях: {used_variables}")

            # Проверка на недоопределённость системы
            # Строим график для первого уравнения
            self.eq = expressions[0]
            self.vars_list = list(self.eq.free_symbols)

            if len(self.vars_list) == 2:
                self.var1, self.var2 = self.vars_list[0], self.vars_list[1]
                self.plot_equation()
                return
            else:
                raise TooManyVariablesError(
                f"adopt_plot поддерживает только 2D-графики. Получено {len(self.vars_list)} переменных: {self.vars_list}. "
                f"Если вам нужен 3D-график, подождите следующей версии!"
            )





        # Обновляем историю

        except Exception as e:
            raise Exception(e)

    def plot_equation(self):
        try:
            def has_odz(expr, var):
                """
                Проверяет, есть ли у выражения ограничения на область допустимых значений (ОДЗ).
                Если есть - лучше рисовать через plot_implicit.
                """
                # 1. Проверяем наличие нелинейных функций с ограничениями (log, sqrt, asin, acos)
                # В SymPy log и ln — одно и то же.
                if expr.has(log) or expr.has(sqrt) or expr.has(asin) or expr.has(acos):
                    return True

                # 2. Проверяем, есть ли переменная в знаменателе (деление на ноль)
                numer, denom = expr.as_numer_denom()
                if var in denom.free_symbols:
                    return True

                return False


            expr = self.eq.lhs - self.eq.rhs
            vars_list = sorted(self.eq.free_symbols, key=lambda s: str(s))
            var1, var2 = vars_list[0], vars_list[1]
            # === 1. Безопасный поиск пересечений (ловит ошибки abs) ===
            x_intercepts = []
            y_intercepts = []
            try:
                x_sol = solve(expr.subs(var2, 0), var1)
                x_intercepts = [float(s) for s in x_sol if s.is_real]
            except Exception:
                pass  # Если sympy не может решить (abs), пропускаем

            try:
                y_sol = solve(expr.subs(var1, 0), var2)
                y_intercepts = [float(s) for s in y_sol if s.is_real]
            except Exception:
                pass


            def zoom_key_handler(event):
                # Проверяем, что нажатие произошло на оси и это сочетание с Ctrl
                if event.inaxes != self.ax:
                    return

                # Коэффициент масштабирования (1.2 = 120%, 0.8 = 80%)
                scale_factor = 1.2

                # Получаем текущие границы
                cur_xlim = self.ax.get_xlim()
                cur_ylim = self.ax.get_ylim()

                # Вычисляем центр текущего обзора
                x_center = (cur_xlim[0] + cur_xlim[1]) / 2
                y_center = (cur_ylim[0] + cur_ylim[1]) / 2

                # Длина текущего диапазона
                cur_xrange = cur_xlim[1] - cur_xlim[0]
                cur_yrange = cur_ylim[1] - cur_ylim[0]
                # print(event.key)
                # Если нажато Ctrl + (или Ctrl + =) — приближаем
                if event.key == 'ctrl+plus' or event.key == 'ctrl+equal' or event.key == 'ctrl+=' or event.key == 'ctrl++':
                    new_xrange = cur_xrange / scale_factor
                    new_yrange = cur_yrange / scale_factor
                # Если нажато Ctrl - — отдаляем
                elif event.key == 'ctrl+minus' or event.key == 'ctrl+-':
                    new_xrange = cur_xrange * scale_factor
                    new_yrange = cur_yrange * scale_factor
                else:
                    return  # Если нажата другая клавиша, ничего не делаем

                # Устанавливаем новые границы, центрируя обзор
                self.ax.set_xlim([x_center - new_xrange / 2, x_center + new_xrange / 2])
                self.ax.set_ylim([y_center - new_yrange / 2, y_center + new_yrange / 2])

                # Принудительно перерисовываем график
                event.canvas.draw_idle()
            # === 2. Увеличиваем разрешение для гладкости (было 500, стало 1000) ===
            if self.lib == 'implicit' or (has_odz(expr, var1) and self.lib is None):
                from sympy.plotting import plot_implicit
                self.current_engine = 'implicit'
                if isinstance(self.limit, (int, float)):
                    self.p = plot_implicit(self.eq, (var1, -self.limit, self.limit), (var2, -self.limit, self.limit), show=False, n=self.n, depth=self.depth, line_color=self.color)
                elif isinstance(self.limit, tuple):
                    if len(self.limit) == 4:
                        self.p = plot_implicit(self.eq, (var1, *self.limit[:2]), (var2, *self.limit[2:]), show=False, n=self.n, depth=self.depth, line_color=self.color)
                    else:
                        raise ValueError(f"Length mismatch (expected 4), got {len(self.limit)}.")
                else:
                    raise TypeError(f"Type mismatch.\nExpected float | tuple[float, float, float, float], got {type(self.limit)}.")
                self.p.process_series()  # Отрисовываем линию

                self.ax = self.p.ax
                logging.info(f"{self.ax}")
                self.fig = self.p.fig
                if self.interact:
                    self.fig.canvas.mpl_connect('key_press_event', zoom_key_handler)
                x_coords_str = ", ".join([f"({x:.2f}, 0)" for x in x_intercepts]) if x_intercepts else "Нет"
                y_coords_str = ", ".join([f"(0, {y:.2f})" for y in y_intercepts]) if y_intercepts else "Нет"

                # Три пустые линии для легенды (они не видны на графике, но создают текст в легенде)
                self.ax.plot([], [], ' ', label=f"${latex(self.eq)}$")  # Красивое уравнение через LaTeX



                patches = self.ax.patches
                logging.info(f"{patches}")
                # === УНИВЕРСАЛЬНОЕ ИЗМЕНЕНИЕ ТОЛЬКО ГРАФИКА (БЕЗ РАМОК) ===

                # 1. Работаем с контурами и коллекциями (contour/plot_implicit)
                for collection in self.ax.collections:
                    collection.set_linewidth(self.linewidth)
                    collection.set_edgecolor(self.color)

                # 2. Работаем с патчами (заливки в implicit), но пропускаем оси (Spines)
                from matplotlib.spines import Spine
                for patch in self.ax.patches:
                    # Если это рамка — пропускаем
                    if isinstance(patch, Spine):
                        continue
                    patch.set_linewidth(self.linewidth)
                    patch.set_edgecolor(self.color)

                # 3. Работаем с обычными линиями (например, ax.plot)
                for line in self.ax.lines:
                    line.set_linewidth(self.linewidth)
                    line.set_color(self.color)



                # Дальше твой код с точками и оформлением...

                try:
                    if self.points:
                        try:

                            for x in x_intercepts: self.ax.scatter(x, 0, s=60, color='red', marker='o', zorder=5, label=f"Пересечения с X: {x_coords_str}")
                        except:
                            pass
                        try:

                            for y in y_intercepts: self.ax.scatter(0, y, s=60, color='blue', marker='o', zorder=5, label=f"Пересечения с Y: {y_coords_str}")
                        except:
                            pass

                    self.ax.axhline(0, color='black', linewidth=1)
                    self.ax.axvline(0, color='black', linewidth=1)
                    self.ax.set_xlim(self.xlims)
                    self.ax.set_ylim(self.ylims)
                    self.ax.set_xlabel(str(var1))
                    self.ax.set_ylabel(str(var2))
                    if self.text_legend:
                        self.ax.plot([], [], ' ', label=f"{self.text_legend}")
                    if self.legend:
                        self.ax.legend()
                    self.ax.grid(True, linestyle='--', alpha=0.7)
                except Exception as e:
                    logging.warning(f"Ошибка при добавлении оформления на p.ax: {e}")

                self.p.fig.tight_layout()
                self.plt = self.p.plt
                if self.is_show:
                    self.p.plt.show()

                return
            else:
                self.current_engine = 'contour'
                if isinstance(self.limit, (float, int)):

                    x_vals = np.linspace(-self.limit, self.limit, self.n)
                    y_vals = np.linspace(-self.limit, self.limit, self.n)
                elif isinstance(self.limit, tuple):
                    if len(self.limit) == 4:
                        x_vals = np.linspace(self.limit[0], self.limit[1], self.n)
                        y_vals = np.linspace(self.limit[2], self.limit[3], self.n)
                    else:
                        raise ValueError(f"Length mismatch (expected 4), got {len(self.limit)}.")
                else:
                    raise TypeError(f"Type mismatch.\nExpected float | tuple[float, float, float, float], got {type(self.limit)}.")
                y_vals[~np.isfinite(y_vals)] = np.nan
                X, Y = np.meshgrid(x_vals, y_vals)
                f = lambdify((var1, var2), expr, modules='numpy')
                # print(x_vals, y_vals, X, Y, f, sep='\n<------------------------------->\n')
                Z = f(X, Y)
                # print(Z)
                self.fig, self.ax = plt.subplots()
                if self.interact:
                    self.fig.canvas.mpl_connect('key_press_event', zoom_key_handler)
                x_coords_str = ", ".join([f"({x:.2f}, 0)" for x in x_intercepts]) if x_intercepts else "Нет"
                y_coords_str = ", ".join([f"(0, {y:.2f})" for y in y_intercepts]) if y_intercepts else "Нет"
                self.ax.contour(X, Y, Z, levels=[0], colors=self.color, linewidths=self.linewidth)

                self.ax.plot([], [], ' ', label=f"Уравнение: ${latex(self.eq)}$")

                # Оси X и Y
                self.ax.axhline(0, color='black', linewidth=1)
                self.ax.axvline(0, color='black', linewidth=1)

                # Точки пересечения (теперь они не вызовут ошибку, если не найдутся)
                self.ax.scatter([x for x in x_intercepts], [0] * len(x_intercepts), s=60, color='red', marker='o', zorder=5,
                           label=f"Пересечения с X: {x_coords_str}")

                self.ax.scatter([0] * len(y_intercepts), [y for y in y_intercepts], s=60, color='blue', marker='o', zorder=5,
                           label=f"Пересечения с Y: {y_coords_str}")

                # Подписи осей строго по переменным
                self.ax.set_xlabel(str(var1))
                self.ax.set_ylabel(str(var2))
                self.ax.grid(True, linestyle='--', alpha=0.7)
                self.ax.set_xlim(self.xlims)
                self.ax.set_ylim(self.ylims)
                if self.text_legend:
                    self.ax.plot([], [], ' ', label=f"{self.text_legend}")
                if self.legend:
                    self.ax.legend()
                self.plt = plt

                if self.is_show:

                    self.plt.show()

        except Exception as e1:
            logging.warning(f"Matplotlib contour не сработал: {e1}")
            # Если контур упал (сингулярности), используем sympy.plot_implicit
            from sympy.plotting import plot_implicit
            p = plot_implicit(self.eq, (var1, -10, 10), (var2, -10, 10), show=False)
            p.show()
    def show(self):
        try:
            if hasattr(self, 'plt'):
                self.plt.show()
            else:
                raise PltNotFoundError("plt Not Found")
        except Exception as e:
            raise Exception(e)
    def save(self, path, dpi: int = 300, format: str | None = None, bbox_inches: Literal['tight', 'standard', None] = 'tight', pad_inches: float | int = 0, transparent: bool = False, orientation: Literal['landscape', 'portrait']='landscape', metadata=None):
        try:
            if hasattr(self, 'fig'):
                self.fig.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches, transparent=transparent, orientation=orientation, metadata=metadata)
            else:
                raise PltNotFoundError("fig not found")
        except Exception as e:
            raise Exception(e)