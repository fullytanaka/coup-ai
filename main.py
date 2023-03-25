import tkinter as tk

class Main():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Main")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.root.destroy()

if __name__ == "__main__":
    Main()