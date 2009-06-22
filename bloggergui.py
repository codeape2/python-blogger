import blogger
import Tkinter as Tk
import sys

def gui_login(toplevel):
    result = [(None, None)]

    def ok_click():
        result[0] = username.get(), password.get()
        dlg.destroy()

    dlg = Tk.Toplevel(toplevel)
    dlg.title("Log in")

    Tk.Label(dlg, text="User name").grid(column=0, row=0)
    Tk.Label(dlg, text="Password").grid(column=0, row=1)
    username = Tk.Entry(dlg)
    password = Tk.Entry(dlg, show="*")
    username.grid(column=1, row=0)
    password.grid(column=1, row=1)

    Tk.Button(dlg, text="OK", command=ok_click).grid(column=0, row=2)

    dlg.wait_window()
    return result[0]
    
if __name__ == '__main__':
    toplevel = Tk.Tk()
    username, password = gui_login(toplevel)
    if not username:
        sys.exit(0)
    service = blogger.login(username, password)
    toplevel.mainloop()
