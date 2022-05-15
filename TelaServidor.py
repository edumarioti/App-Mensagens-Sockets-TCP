from tkinter import *


class TelaServidor(Frame):

    def __init__(self, servidor):
        super().__init__()
        self.servidor = servidor
        
        self.master.title("Sockets TCP - Servidor")
        self.grid(row=0, column=0)

        self.lfLogs = LabelFrame(self, text="Logs")
        self.lfLogs.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)
        
        self.textLogs = Text(self.lfLogs, state=DISABLED, width=125)
        self.textLogs.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)
        
        self.lfTituloConectados = LabelFrame(self, text="Conectados")
        self.lfTituloConectados.grid(row=0, column=1, padx=5, pady=5, sticky=E+W+S+N)
        
        self.lbConectados = Listbox(self.lfTituloConectados, height=24)
        self.lbConectados.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)


    def atualizaLista(self):
        
        self.lbConectados.delete(0, END)
        
        if self.servidor.usuarios:
            
            for usuario in self.servidor.usuarios:
                self.lbConectados.insert(END, usuario)
    
    def atualizaLogs(self, logs):
        self.textLogs.config(state=NORMAL)
        self.textLogs.insert(END, str(logs))  
        self.textLogs.config(state=DISABLED)
        
        
        
        




