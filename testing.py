import tkinter as tk


class SimpleWindow(tk.Tk):
    def __init__(self):
        super().__init__()  # 显式调用父类 __init__ (虽然 tk.Tk 会自动调用)
        self.title("Simple Test Window")
        tk.Label(self, text="Hello, Tkinter!").pack()


if __name__ == "__main__":
    app = SimpleWindow()
    app.mainloop()
