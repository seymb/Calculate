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
        self.root.geometry('360x600')
        icon = PhotoImage(file = "Calculator.png")
        self.root.iconphoto(False, icon)
        self.root.configure(background='black')
        
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
        self.label = ttk.Label(master, text='', font=('Segoe UI', 20), background='black', foreground='white')
        self.label.pack(anchor=E)
        self.result = ttk.Label(master, text='', font=('Segoe UI', 40), background='black', foreground='white')
        self.result.pack(anchor=E)
        self.temp_num = []
        self.input_string = ''
        self.flag = '' #запоминаем какая последняя скобка было введена
        self.var = [] #стек
        self.calculatorlogic = calculatorlogic

    def update_display(self, value):
        self.result.config(text=value)

    def add_to_input(self, value):
        if value.isdigit() or (value == '.' and self.input_string):
            self.input_string += value
            self.update_display(self.input_string)
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
        elif value == 'C':
            self.input_string = ''
            self.flag = '' # очищаем иначе он будет думать что скобка уже существует
            self.temp_num = []
            self.label.config(text='')
            self.result.config(text='')
        elif value in 'x²√': # ДОРАБОТАТЬ
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
        elif value == '()':
            #Скобки добавляются правильно, скобка добавится если он первый элемент, а так 
            # же не закроет если последним элементом будем операция вычисления
            if '(' != self.flag and (not self.input_string or self.input_string[-1] in '+-÷*'):
                self.input_string += '('
                self.flag = '('
            elif self.flag == '(' and self.input_string[-1] not in '+-÷*' and self.input_string[-1].isdigit():
                self.input_string += ')'
                self.flag = ')'
            self.update_display(self.input_string)
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
                if self.flag == '(':
                    self.input_string += ')'
                self.label.config(text=self.input_string)
                self.temp_var = ''
                s = self.input_string.replace('²', 'x') #заменяем для того что прошло вычиселение в calculatorlogic
                for i in range(len(s)):
                    if (i+1 < len(s)) and (s[i-1] == '(' or i == 0) and s[i] == '-' and s[i+1].isdigit(): # s[i] != '('
                        self.temp_var += s[i]
                    elif s[i].isdigit() or s[i] == '.':
                        self.temp_var += s[i]
                    elif s[i] == '(':
                        self.var.append(self.temp_num)
                        self.temp_num = []
                    elif s[i] == ')':
                        if self.temp_var:
                            self.temp_num.append(float(self.temp_var))
                            self.temp_var = ''
                        if len(self.temp_num) > 2 or '√' in self.temp_num or 'x' in self.temp_num:
                            result = self.calculatorlogic.calculate(self.temp_num)
                        else:
                            # result = int(self.temp_num[0]) if isinstance(self.temp_num[0], int) else self.temp_num[0]
                            result = self.temp_num[0] # Есть мысль что она работает также эффективно как и сверху
                        self.temp_num = self.var.pop()
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
                else:
                    self.update_display(str(result))
                    self.temp_num = []
                    self.input_string = str(result)

    

class Keypad:
    # Создает и размещает кнопки
    # Обрабатывает нажатия и передает команды в Display
    def __init__(self, master, display, calculatorlogic):
        self.frame = ttk.Frame(master)
        self.frame.pack(side=BOTTOM, fill=BOTH)
        self.display = display
        self.calculatorlogic = calculatorlogic

        nums = {
                0:{'number': '0', 'row':4, 'col': 1},
                1:{'number': '1', 'row':3, 'col': 0},
                2:{'number': '2', 'row':3, 'col': 1},
                3:{'number': '3', 'row':3, 'col': 2},
                4:{'number': '4', 'row':2, 'col': 0},
                5:{'number': '5', 'row':2, 'col': 1},
                6:{'number': '6', 'row':2, 'col': 2},
                7:{'number': '7', 'row':1, 'col': 0},
                8:{'number': '8', 'row':1, 'col': 1},
                9:{'number': '9', 'row':1, 'col': 2},
                10:{'number': '.', 'row':4, 'col': 0},
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


        for i in nums:
            self.btn = ttk.Button(self.frame, style='Num_Button.TButton', takefocus=0, text=nums[i]['number'], command=lambda t=nums[i]['number']: self.on_button_click(t))
            self.btn.grid(row=nums[i]['row'], column=nums[i]['col'], ipady=20, sticky=NSEW)

        for i in oper:
            self.btn = ttk.Button(self.frame, style='Oper_Button.TButton', takefocus=0, text=oper[i]['text'], command=lambda t=oper[i]['text']: self.on_button_click(t))
            self.btn.grid(row=oper[i]['row'], column=oper[i]['col'], ipady=20, sticky=NSEW)
        
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
        except:
            return 'Не определено'
        return int(result) if result.is_integer() else float('{:.7f}'.format(result))


    

if __name__== '__main__':
    calc = CalculatorApp()
    calc.run()
