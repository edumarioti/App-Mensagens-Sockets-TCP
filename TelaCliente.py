from datetime import datetime
import os
import threading
from time import sleep
from tkinter import filedialog, messagebox
from tkinter import *
from cliente import Cliente
from objetosCominicacao import *

            
class TelaAplicacao(Frame):

    def __init__(self):
        super().__init__()
        
        self.master.title("Sockets TCP - Cliente")
        self.grid(row=0, column=0)

        self.lfTituloMsgRecebida = LabelFrame(self, text="Mensagens Recebidas", width=80)
        self.lfTituloMsgRecebida.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)
        
        self.textMsgRecebida = Text(self.lfTituloMsgRecebida, state=DISABLED, width=75)
        self.textMsgRecebida.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)
        
        self.lfTituloConectados = LabelFrame(self, text="Conectados")
        self.lfTituloConectados.grid(row=0, column=1, padx=5, pady=5, sticky=E+W+S+N)
        
        self.lbConectados = Listbox(self.lfTituloConectados, height=24)
        self.lbConectados.grid(row=0, column=0, padx=5, pady=5, sticky=E+W+S+N)

        self.lfMsgEnviar =  LabelFrame(self, text="Envio de Mensagens")
        self.lfMsgEnviar.grid(row=1, rowspan=2, column=0, padx=5, pady=5, sticky=E+W+S+N)
        
        self.entryMsgEnviar = Entry(self.lfMsgEnviar, width=100, state=DISABLED)
        self.entryMsgEnviar.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=E+W)
                
        self.buttonEnviar = Button(self.lfMsgEnviar, text="Enviar", state=DISABLED, width=15)
        self.buttonEnviar.grid(row=1, column=0, padx=5, pady=5, sticky=W+E+S+N)
        self.buttonEnviar["command"] = self.validarMensagem
        
        self.buttonselecionarArquivo = Button(self.lfMsgEnviar, text="Carregar arquivo", state=DISABLED, width=15)
        self.buttonselecionarArquivo.grid(row=1, column=1, padx=5, pady=5, sticky=E+W+S+N)
        self.buttonselecionarArquivo["command"] = self.selecionarArquivo
        
        self.buttonEnviarArquivo = Button(self.lfMsgEnviar, text="Enviar arquivo", state=DISABLED, width=15)
        self.buttonEnviarArquivo.grid(row=1, column=2, padx=5, pady=5, sticky=E+W+S+N)
        self.buttonEnviarArquivo["command"] = self.enviarArquivo
        
        self.lfAcoesUsuario = LabelFrame(self, text="Usuário")
        self.lfAcoesUsuario.grid(row=2, rowspan=2, column=1, columnspan=2, padx=5, pady=5, sticky=E+W+S+N)
        
        self.entryUsuario = Entry(self.lfAcoesUsuario)
        self.entryUsuario.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=E+W)
        
        self.buttonLogin = Button(self.lfAcoesUsuario, text="Login")
        self.buttonLogin.grid(row=1, column=0, padx=5, pady=5, sticky=E+W+S+N)
        self.buttonLogin["command"] = self.login
        
        self.buttonLogout = Button(self.lfAcoesUsuario, text="Logout", state=DISABLED)
        self.buttonLogout.grid(row=1, column=1, padx=5, pady=5, sticky=E+W+S+N)
        self.buttonLogout["command"] = self.logout
        
        # Cria um cliente e conecta no servidor
        self.cliente = Cliente()
        self.cliente.conectar()
        
        # Inicia a thread para de scan de variaveis
        self.threadScan = ThreadScanservidor(self)
        self.threadScan.start()

        self.usuariosAtivos = []
        self.mensagens= []

    def login(self):
        
        usuario = self.entryUsuario.get()
        usuario = str(usuario).strip()

        usuario_valido = (usuario != "")

        if usuario_valido:
            self.cliente.login(usuario)
            self.seUsuarioLogadoAtivaOsCampos()
            messagebox.showinfo("Confirmação", "Usuário conectado com sucesso!")
            
        else:
            messagebox.showerror("Erro", "O usuário não é válido") 
  
    def logout(self):
        
        self.cliente.logout()
        self.seUsuarioLogadoAtivaOsCampos()
        self.entryUsuario.delete(0, END)
        messagebox.showinfo("Desconectar", "Usuário desconectado!")

    def validarMensagem(self):
        mensagem = self.entryMsgEnviar.get()
        mensagem = mensagem.strip()
        
        mensagem_valida = (mensagem != '')
        
        destinatario = ''
        
        try:
            destinatario = self.lbConectados.selection_get()
            destinatario = destinatario.strip()
            
            destinatario_valido = (destinatario != '')
        
            if mensagem_valida and destinatario_valido:
                    self.enviarMensagem(mensagem=mensagem, destinatario=destinatario)
                    self.entryMsgEnviar.delete(0, END)               
            else:
                messagebox.showerror("Invalido", "A mensagem não pode ser vazia!")
        except:
            messagebox.showerror("Invalido", "Selecione um remetente conectado!")
                
    def enviarMensagem(self, mensagem, destinatario):
        
        data_agora = datetime.now()
        data = data_agora.strftime("%d-%m-%Y")
        hora = data_agora.strftime("%H:%M:%S")
        
        self.insereMensagem(f"{data} {hora} | {mensagem} -> {destinatario} \n")
        
        self.cliente.enviar(acao=MENSAGEM, mensagem=mensagem, destinatario=destinatario)
    
    def selecionarArquivo(self):
              
        pathArquivo = filedialog.askopenfilename(
                                    initialdir="/",
                                    title="Escolha um arquivo",
                                    filetypes=(("jpeg files", "*.jpg"),("all files", "*.*"))
                                    )
        if pathArquivo:
            nomeArquivo = os.path.basename(pathArquivo)

            confirmação = messagebox.askokcancel("Confirmação", f"Deseja carregar o arquivo '{nomeArquivo}'?")
            
            if confirmação:

                self.threadEnviarArquivo = ThreadEnviarArquivo(self, pathArquivo, nomeArquivo)
                self.threadEnviarArquivo.start()
          
    def solicitaEnvioArquivo(self, pathArquivo, nomeArquivo):
        
        data_agora = datetime.now()
        data = data_agora.strftime("%d-%m-%Y")
        hora = data_agora.strftime("%H:%M:%S")
        
        self.nomeArquivo = nomeArquivo
        
        self.cliente.enviar(RECEBER_ARQUIVO, nomeArquivo)
        self.cliente.enviarArquivo(pathArquivo)
        sleep(5)
        
        self.insereMensagem(f"{data} {hora} | '{self.nomeArquivo}' -> Arquvio carregado e pronto para envio!\n")
            
        self.cliente.enviar(acao=ARQUIVO, mensagem=self.nomeArquivo)
        self.buttonEnviarArquivo.config(state=NORMAL)
                
    def enviarArquivo(self):
        
        try:
            
            destinatario = self.lbConectados.selection_get()
            destinatario = destinatario.strip()
                
            destinatario_valido = (destinatario != '')
            
            if destinatario_valido:
                    
                data_agora = datetime.now()
                data = data_agora.strftime("%d-%m-%Y")
                hora = data_agora.strftime("%H:%M:%S")
                
                self.insereMensagem(f"{data} {hora} | '{self.nomeArquivo}' -> {destinatario} \n")
                
                self.cliente.enviar(acao=ARQUIVO, mensagem=self.nomeArquivo, destinatario=destinatario)
                self.buttonEnviarArquivo.config(state=DISABLED)
        except:
            messagebox.showerror("Invalido", "Primeiro selecione um usuaário conectado!")
        
    def receberArquivo(self, nomeArquivo):
        # solicita ao usuário onde deseja salvar o arquivo recebido
        path = filedialog.askdirectory(initialdir=os.getcwd(), title=f"Salvar '{nomeArquivo}' em:")

        # cria um novo arquivo binario, vazio, para receber o arquivo enviado
        arquivo = open(path + '/' + nomeArquivo, "wb")

        # Receba as partes do arquivo e monta o arquivo
        dadosArquivo = self.cliente.mySocket.recv(1024)

        while dadosArquivo:

            arquivo.write(dadosArquivo)
            dadosArquivo = self.cliente.mySocket.recv(1024)
        
        arquivo.close()
        
        messagebox.showinfo("Sucesso", "O arquivo foi transferido com sucesso!")
        
    def scanServidor(self):
        
        while True:
        
            if self.cliente.conectado:

                objetoRecebido = self.cliente.verificarRespostaServidor()
                
                if objetoRecebido != None:  

                        if objetoRecebido.usuariosAtivos != None:
                            self.atualizaListaUsuarios(objetoRecebido.usuariosAtivos)
                        
                        if objetoRecebido.mensagensRecebidas != '':
                            self.insereMensagem(objetoRecebido.mensagensRecebidas)
                            
                        if objetoRecebido.nomeArquivo != '':
                            self.receberArquivo(objetoRecebido.nomeArquivo)
                                                                
    def atualizaListaUsuarios(self, usuariosAtivos:list):
        
        if self.usuariosAtivos != usuariosAtivos:

            self.usuariosAtivos = usuariosAtivos
            
            self.lbConectados.delete(0, END)
            
            for usuario in self.usuariosAtivos:
        
                if usuario != self.cliente.usuario:
                    self.lbConectados.insert(END, usuario)

            if len(self.usuariosAtivos) > 2:
                self.lbConectados.insert(END, "Todos")
    
    def insereMensagem(self, mensagem=str):
        self.textMsgRecebida.config(state=NORMAL)
        self.textMsgRecebida.insert(END, mensagem)  
        self.textMsgRecebida.config(state=DISABLED)
        
    def seUsuarioLogadoAtivaOsCampos(self):
         
        if self.cliente.logado:

            self.buttonEnviar.config(state=NORMAL)
            self.buttonselecionarArquivo.config(state=NORMAL)
            self.buttonLogout.config(state=NORMAL)
            self.entryMsgEnviar.config(state=NORMAL)
            self.buttonLogin.config(state=DISABLED)
            self.entryUsuario.config(state=DISABLED)
                                   
        else:
            
            self.buttonEnviar.config(state=DISABLED)
            self.buttonselecionarArquivo.config(state=DISABLED)
            self.buttonLogout.config(state=DISABLED)
            self.entryMsgEnviar.config(state=DISABLED)
            self.buttonLogin.config(state=NORMAL)
            self.entryUsuario.config(state=NORMAL)
                              
    def pararThread(self):
        self.kill.set()

class ThreadScanservidor(threading.Thread):
    
    def __init__(self, telaAplicacao:TelaAplicacao):
        threading.Thread.__init__(self)
        self.kill = threading.Event()
        self.telaAplicacao = telaAplicacao
        
    def run(self):
        
        while not self.kill.is_set():
            sleep(1)           
            self.telaAplicacao.scanServidor()
  
    def pararThread(self):
        self.kill.set()

class ThreadEnviarArquivo(threading.Thread):
    
    def __init__(self, telaAplicacao:TelaAplicacao, pathArquivo, nomeArquivo):
        threading.Thread.__init__(self)
        self.telaAplicacao = telaAplicacao
        self.pathArquivo = pathArquivo
        self.nomeArquivo = nomeArquivo

        
    def run(self):
        self.telaAplicacao.solicitaEnvioArquivo(self.pathArquivo, self.nomeArquivo)

   
def fechar():
    
    sair = messagebox.askokcancel("Fechar", "Tem certeza que deseja sair?")
    
    if sair:
        
        app.threadScan.pararThread()
        
        sleep(0.1)
        if app.cliente.logado:
            app.cliente.logout()
        
        sleep(0.1)
        if app.cliente.conectado:
            app.cliente.desconectar()
        
        sleep(0.2)
        root.destroy()
        
        sleep(0.2)
        exit(1)

if __name__ == '__main__':
    
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", fechar)
    app = TelaAplicacao()
    root.resizable(width=0, height=0)
    root.mainloop()




