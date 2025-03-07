from tkinter import *
from tkinter import ttk
from tkinter import font
import math

class CalculatorApp:
    # Создает новое окно
    # Управляет темой и стилем
    # Запускает приложение
    def __init__(self):
        self.root = Tk()
        self.root.title('Calculator')
        self.root.geometry('400x600')
        icon = PhotoImage(file = "Calculator.png")
        self.root.iconphoto(False, icon)
        self.root.configure(background='black')
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Num_Button.TButton', font=('Segoe UI', 20), foreground="white", background='gray', relief='flat')
        self.style.configure('Oper_Button.TButton', font=('Segoe UI', 20), foreground="white", background='orange', relief='flat')
        
        self.calculatorlogic = CalculatorLogic()
        self.display = Display(self.root, self.calculatorlogic)
        self.keypad = Keypad(self.root, self.display, self.calculatorlogic)


    def run(self):
        self.root.mainloop()


class Display:
    # Показывает ввод пользователя
    # Обновляется при нажатии кнопок
    def __init__(self, master, calculatorlogic):
        self.label = ttk.Label(master, text='', font=('Segoe UI', 25), background='black', foreground='white')
        self.label.pack(anchor=E)
        self.result = ttk.Label(master, text='', font=('Segoe UI', 40), background='black', foreground='white')
        self.result.pack(anchor=E)
        self.temp_num = []
        self.input_string = ''
        self.flag_brackets = '' #запоминаем какая последняя скобка было введена
        self.stack_brackets = [] #стек
        self.calculation_done = False  # Флаг для отслеживания, что вычисление завершено
        self.calculatorlogic = calculatorlogic

    def update_display(self, value):
        self.result.config(text=value)

    def all_clear(self):
        self.input_string = ''
        self.flag_brackets = '' # очищаем иначе он будет думать что скобка уже существует
        self.temp_num = []
        self.label.config(text='')
        self.result.config(text='')
        self.calculation_done = False

    def add_to_input(self, value):
        # Когда после "Не определено" вводится число
        if self.result["text"] == "Не определено":
            self.all_clear()
            self.input_string = value
            self.update_display(self.input_string)
            return
        # Когда после результата (числа) введена цифра
        if self.calculation_done and value.isdigit():
            self.input_string = value
            self.label.config(text='')
            self.update_display(self.input_string)
            self.calculation_done = False  # Сбрасываем флаг после ввода цифры
            return
        
        # Если результат - число (включая отрицательные), и введен операнд, продолжаем вычисление
        if self.result["text"].replace('-', '').isdigit() and value in '+-÷*':
            self.input_string += value
            self.update_display(self.input_string)
            self.calculation_done = False  # Сбрасываем флаг после ввода операнда
            return
        
        # Обработка ввода чисел
        if value.isdigit() or (value == '.' and self.input_string):
            self.input_string += value
            self.update_display(self.input_string)
        
        # Обработка операндов
        elif value in '+-÷*':
            if self.input_string and '(' in self.input_string:
                if value == '-' and self.input_string[-1] != '-':
                    self.input_string += value
                    self.update_display(self.input_string)
                if self.input_string and self.input_string[-1] not in '+-÷*(':
                    self.input_string += value
                    self.update_display(self.input_string)
            else:
                if not self.input_string and value == '-':
                    self.input_string += value
                    self.update_display(self.input_string)
                if self.input_string and self.input_string[-1] not in '+-÷*':
                    self.input_string += value
                    self.update_display(self.input_string)
        
        # Если нажали 'C', очищаем все
        elif value == 'C':
            self.all_clear()
        
        # Обработка квадратов и корней
        elif value in 'x²√':
            if self.input_string and self.input_string[-1] not in '+-÷*':
                if value == 'x²' and self.input_string[-1] != '²':
                    self.input_string += '²'
                elif value == '√':
                    if self.input_string and self.input_string[-1] == ')':
                        count = 1
                        i = len(self.input_string) - 2
                        while i >= 0 and count > 0:
                            if self.input_string[i] == ')':
                                count += 1
                            elif self.input_string[i] == '(':
                                count -= 1
                            i -= 1
                        self.input_string = self.input_string[:i+1] + f'√{self.input_string[i+1:]}'
                    else:
                        # Найти последнее число
                        i = len(self.input_string) - 1
                        while i >= 0 and (self.input_string[i].isdigit() or self.input_string[i] == '.' or 
                                        (self.input_string[i] == '-' and (i == 0 or self.input_string[i-1] in '+-*/÷('))):
                            i -= 1
                        # Заменить последнее число на √(число)
                        last_number = self.input_string[i+1:]
                        if last_number:
                            self.input_string = self.input_string[:i+1] + f'√({last_number})'
            self.update_display(self.input_string)

        # Обработка скобок
        elif value == '()':
            if '(' != self.flag_brackets and (not self.input_string or self.input_string[-1] in '+-÷*'):
                self.input_string += '('
                self.flag_brackets = '('
            elif self.flag_brackets == '(' and self.input_string[-1] not in '+-÷*' and self.input_string[-1].isdigit():
                self.input_string += ')'
                self.flag_brackets = ')'
            self.update_display(self.input_string)

        # Обработка равенства
        elif value == '=':
            if (self.input_string and 
                    self.input_string[-1] not in '+-÷*' and
                    ('+' in self.input_string or 
                    ('-' in self.input_string[2:] if '(' in self.input_string else '-' in self.input_string[1:]) or 
                    '÷' in self.input_string or 
                    '*' in self.input_string or
                    '²' in self.input_string or
                    '√' in self.input_string)
                ):
                if self.flag_brackets == '(':
                    self.input_string += ')'
                self.label.config(text=self.input_string)
                self.temp_var = ''
                s = self.input_string.replace('²', 'x') #заменяем для того что прошло вычиселение в calculatorlogic
                for i in range(len(s)):
                    if (i+1 < len(s)) and (s[i-1] == '(' or i == 0) and s[i] == '-' and s[i+1].isdigit():
                        self.temp_var += s[i]
                    elif s[i].isdigit() or s[i] == '.':
                        self.temp_var += s[i]
                    elif s[i] == '(':
                        self.stack_brackets.append(self.temp_num)
                        self.temp_num = []
                    elif s[i] == ')':
                        if self.temp_var:
                            self.temp_num.append(float(self.temp_var))
                            self.temp_var = ''
                        if len(self.temp_num) > 2 or '√' in self.temp_num or 'x' in self.temp_num:
                            result = self.calculatorlogic.calculate(self.temp_num)
                        else:
                            result = self.temp_num[0]
                        self.temp_num = self.stack_brackets.pop()
                        self.temp_num.append(result)
                    else:
                        if self.temp_var:
                            self.temp_num.append(float(self.temp_var))
                            self.temp_var = ''
                        self.temp_num.append(s[i])
                if self.temp_var:
                    self.temp_num.append(float(self.temp_var))
                if len(self.temp_num) > 1:
                    result1 = self.calculatorlogic.calculate(self.temp_num)
                    self.update_display(str(result1))
                    self.temp_num = []
                    self.input_string = str(result1)
                    self.calculation_done = True
                else:
                    self.update_display(str(result))
                    self.temp_num = []
                    self.input_string = str(result)
                    self.calculation_done = True

    

class Keypad:
    # Создает и размещает кнопки
    # Обрабатывает нажатия и передает команды в Display
    def __init__(self, master, display, calculatorlogic):
        self.frame = ttk.Frame(master)
        self.frame.pack(side=BOTTOM, fill=BOTH)
        self.display = display
        self.calculatorlogic = calculatorlogic

        nums = {
                0:{'text': '0', 'row':4, 'col': 1},
                1:{'text': '1', 'row':3, 'col': 0},
                2:{'text': '2', 'row':3, 'col': 1},
                3:{'text': '3', 'row':3, 'col': 2},
                4:{'text': '4', 'row':2, 'col': 0},
                5:{'text': '5', 'row':2, 'col': 1},
                6:{'text': '6', 'row':2, 'col': 2},
                7:{'text': '7', 'row':1, 'col': 0},
                8:{'text': '8', 'row':1, 'col': 1},
                9:{'text': '9', 'row':1, 'col': 2},
                10:{'text': '.', 'row':4, 'col': 0},
                }
        
        oper = {0:{'text': '=', 'row':4, 'col': 3},
                1:{'text': '()', 'row':4, 'col': 2},
                2:{'text': '+', 'row':3, 'col': 3},
                3:{'text': '-', 'row':2, 'col': 3},
                4:{'text': '*', 'row':1, 'col': 3},
                5:{'text': '÷', 'row':0, 'col': 3},
                6:{'text': 'x²', 'row':0, 'col': 2},
                7:{'text': '√', 'row':0, 'col': 1},
                8:{'text': 'C', 'row':0, 'col': 0},
                }
        
        for i in range(4):
            self.frame.columnconfigure(index=i, weight=1)
            self.frame.rowconfigure(index=i, weight=1)
            
        self.create_buttons(nums, 'Num_Button.TButton')
        self.create_buttons(oper, 'Oper_Button.TButton')
            
    def create_buttons(self, button_data, button_style):
        for i in button_data:
            self.btn = ttk.Button(self.frame, style=button_style, takefocus=0, text=button_data[i]['text'], command=lambda t=button_data[i]['text']: self.on_button_click(t))
            self.btn.grid(row=button_data[i]['row'], column=button_data[i]['col'], ipady=20, sticky=NSEW)


        
    def on_button_click(self, value):
        self.display.add_to_input(value)
    

class CalculatorLogic:
    # Обработка арифметических операций
    # Проверяет корректность выражения
    # Выводит результат или ошибку
    def __init__(self):
        self.operation = {'+': lambda a, b: a + b,
                          '*': lambda a, b: a * b,
                          '÷': lambda a, b: a / b,
                          '-': lambda a, b: a - b,
                          'x': lambda a: math.pow(a, 2),
                          '√': lambda a: math.sqrt(a)}

    def calculate(self, value):
        stack_nums = []  # Используем стек для сбора чисел
        stack_oper= []  # Используем стек для сбора операндов
        try:
            for i in value:
                if isinstance(i, (float, int)):
                    stack_nums.append(i)
                elif i in ['x', '√']:
                    if i == 'x':
                        a = stack_nums.pop()
                        result = self.operation[i](a)
                        stack_nums.append(result)
                    else:
                        stack_oper.append(i)
                elif i in ['*', '÷']:
                    if stack_oper and stack_oper[-1] == '√':
                        a = stack_nums.pop()
                        oper = stack_oper.pop()
                        result = self.operation[oper](a)
                        stack_nums.append(result)
                    elif stack_oper and stack_oper[-1] in ['*', '÷']:
                        b = stack_nums.pop()
                        a = stack_nums.pop()
                        oper = stack_oper.pop()
                        result = self.operation[oper](a, b)
                        stack_nums.append(result)
                    stack_oper.append(i)
                elif i in ['+', '-']:
                    if stack_oper and stack_oper[-1] == '√':
                        a = stack_nums.pop()
                        oper = stack_oper.pop()
                        result = self.operation[oper](a)
                        stack_nums.append(result)
                    elif stack_oper and stack_oper[-1] in ['*', '÷']:
                        b = stack_nums.pop()
                        a = stack_nums.pop()
                        oper = stack_oper.pop()
                        result = self.operation[oper](a, b)
                        stack_nums.append(result)
                    elif stack_oper and stack_oper[-1] in ['+', '-']:
                        b = stack_nums.pop()
                        a = stack_nums.pop()
                        oper = stack_oper.pop()
                        result = self.operation[oper](a, b)
                        stack_nums.append(result)
                    stack_oper.append(i)
            while stack_oper:
                if len(stack_nums)>1 and '√' not in stack_oper:
                    b = stack_nums.pop()
                    a = stack_nums.pop()
                    oper = stack_oper.pop()
                    result = self.operation[oper](a, b)
                else:
                    a = stack_nums.pop()
                    oper = stack_oper.pop()
                    result = self.operation[oper](a)
                stack_nums.append(result)
            return int(result) if result.is_integer() else float('{:.7f}'.format(result))
        except:
            return 'Не определено'


    

if __name__== '__main__':
    calc = CalculatorApp()
    calc.run()
