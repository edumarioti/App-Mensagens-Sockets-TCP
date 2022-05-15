from ast import literal_eval
from time import sleep
from logs import log
from timeout import timeout
from TelaServidor import TelaServidor
from datetime import datetime
from tkinter import Tk
from objetosCominicacao import *
import socket, pickle, threading
import os


class Servidor(object):
    
    def __init__(self):
             
        self.threadTela = ThreadTela(self)
        self.threadTela.start()

        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketTCP.bind((HOST, PORT))

        print("Servidor iniciado")
        print("Esperando requisições do cliente...")

        self.enderecos = {}
        self.usuarios = []
        self.bufferMensagens = []
        self.bufferArquivos = []
        self.pathTemp = os.path.dirname(os.path.realpath(__file__)) + '/temp'
        
        if not os.path.exists(self.pathTemp):
            os.makedirs(self.pathTemp)

        while True:
    
            self.socketTCP.listen(1)
            self.clienteSocket, self.clienteEndereco = self.socketTCP.accept()
            
            self.threadCliente = ThreadCliente(self.clienteEndereco, self.clienteSocket, self)
            self.threadCliente.name = f"Cliente -> {self.clienteEndereco}"
            self.threadCliente.start()


class ThreadCliente(threading.Thread):
    
    def __init__(self, clienteEndereco, clientsocket, servidor):
        threading.Thread.__init__(self)
        self.clienteSocket = clientsocket
        self.clienteEndereco = clienteEndereco
        self.servidor = servidor
        
        self.usuario = ''
        
        self.mensagemProntaParaEnvio = ''
        self.arquivoProntoParaEnvio = ''
        self.arquivoPronto = False
        
        self.threadAtualizarCliente = ThreadAtualizarCliente(clienteEndereco, clientsocket, servidor)
        self.threadAtualizarCliente.name = f"Atualizar -> {clienteEndereco}"
        self.threadAtualizarCliente.start()
    
    def run(self):
        
        while True:
            sleep(1)
        
            # recebe a mensagem
            dados = self.clienteSocket.recv(4096)
            
            dadosValidos = dados != b''
            
            if dadosValidos:

                #desserializa a mensagem recebida, disponibilizando o objeto novamente na memoria
                objetoRecebido:cliente_para_servidor
                objetoRecebido = pickle.loads(dados)
                
                print(self.usuario, '->', objetoRecebido.acao)

                # Cria as variaveis locais
                usuario = objetoRecebido.remetente
                acao = objetoRecebido.acao
                IpUsuario = self.clienteEndereco
                destinatario = objetoRecebido.destinatario
                mensagem = objetoRecebido.mensagem
                
                print(acao)
                
                if acao == LOGOUT:
                    self.logout(usuario)
                    mensagemLog = log(self.clienteEndereco, self.usuario, acao)
                    self.servidor.app.atualizaLogs(mensagemLog)
                    
                elif acao == LOGIN:
                    self.login(usuario)
                    mensagemLog = log(self.clienteEndereco, self.usuario, acao)
                    self.servidor.app.atualizaLogs(mensagemLog)

                elif acao == MENSAGEM:
                    self.selecionaDestinatario(objetoRecebido)

                elif acao == ARQUIVO:
                    self.adicionaBufferArquivo(objetoRecebido)
                                    
                elif acao == RECEBER_ARQUIVO:
                    self.salvaArquivo(mensagem)
                
                    
                
                self.servidor.app.atualizaLista()
                                     
    def selecionaDestinatario(self, objetoRecebido:cliente_para_servidor):

        remetente = objetoRecebido.remetente

        mensagem = objetoRecebido.mensagem
        
        data_agora = datetime.now()
        data = data_agora.strftime("%d-%m-%Y")
        hora = data_agora.strftime("%H:%M:%S")
        
        mensagemFinal = (f"{data} {hora} | {remetente} -> {mensagem}")

        if objetoRecebido.destinatario == 'Todos':
            
            for usuario in self.servidor.enderecos:
                
                if usuario != self.usuario:
                    endereco = self.servidor.enderecos[usuario]
                    endereco = literal_eval(endereco)

                    self.adicionaBufferMensagem(mensagemFinal, endereco)
                    
                    mensagemLog = log(self.clienteEndereco, self.usuario, MENSAGEM+":"+mensagem, endereco, objetoRecebido.destinatario)
                    self.servidor.app.atualizaLogs(mensagemLog)
        else:
 
            endereco = self.servidor.enderecos[objetoRecebido.destinatario]
            endereco = literal_eval(endereco)
            print(endereco)
            self.adicionaBufferMensagem(mensagemFinal, endereco)
            
            mensagemLog = log(self.clienteEndereco, self.usuario, MENSAGEM+":"+mensagem, endereco, objetoRecebido.destinatario)
            self.servidor.app.atualizaLogs(mensagemLog)
            
   
    
    def adicionaBufferMensagem(self, mensagemFormatada, endereco):
        print(f"adicionei {mensagemFormatada} para {endereco} ")
        self.servidor.bufferMensagens.append((endereco, mensagemFormatada))
     
    def adicionaBufferArquivo(self, objetoRecebido:cliente_para_servidor):
       
        endereco = self.servidor.enderecos[objetoRecebido.destinatario]
        endereco = literal_eval(endereco)
        
        remetente = objetoRecebido.remetente

        nomeArquivo = objetoRecebido.mensagem
        

        
        data_agora = datetime.now()
        data = data_agora.strftime("%d-%m-%Y")
        hora = data_agora.strftime("%H:%M:%S")
        
        mensagemFinal = (f"{data} {hora} | {remetente} -> '{nomeArquivo}'")
        print(f"Mensagem cadastrada -> {endereco}:{mensagemFinal}")
        
        self.servidor.bufferArquivos.append((endereco, nomeArquivo))
        
        mensagemLog = log(self.clienteEndereco, self.usuario, ARQUIVO+":"+nomeArquivo, endereco, objetoRecebido.destinatario)
        self.servidor.app.atualizaLogs(mensagemLog)
            
                                    
    def logout(self, usuario:str):
        
        self.usuario = ''
        self.servidor.usuarios.remove(usuario)
        del self.servidor.enderecos[usuario]
        print ("Logout:", usuario)
    
    def login(self, usuario:str):
        
        if not usuario in self.servidor.usuarios:
            self.usuario = usuario
            self.servidor.enderecos[usuario] = f'{self.clienteEndereco}'
            self.servidor.usuarios.append(usuario)
            
            print (f"Login: {usuario} em {self.servidor.enderecos[usuario]}")
        else:
            print("Usuario já logado")

    def salvaArquivo(self, nomeArquivo):
         
        arquivoTemporario = open(self.servidor.pathTemp + '/' + nomeArquivo, "wb")
        
        # Receba as partes do arquivo e monta o arquivo, esta função travava o processo quando não recebia mais nada
        # utilizando o Timeout foi possivel contornar      
        self.recebeArquivo(arquivoTemporario)

        # Feche o arquivo aberto no lado do servidor uma vez que a cópia seja concluída
        arquivoTemporario.close()
 
    @timeout(3)
    def recebeArquivo(self, arquivoTemporario):
        dadosArquivo = self.clienteSocket.recv(1024)

        while dadosArquivo:
            arquivoTemporario.write(dadosArquivo)
            dadosArquivo = self.clienteSocket.recv(1024)


class ThreadAtualizarCliente(threading.Thread):
    
    def __init__(self, clienteEndereco, clientsocket, servidor:Servidor):
        threading.Thread.__init__(self)
        self.clienteSocket = clientsocket
        self.clienteEndereco = clienteEndereco
        self.servidor = servidor
       

        self.mensagemProntaParaEnvio = ''
        self.arquivoProntoParaEnvio = ''
    
    def run(self):
        
        while True:
            sleep(1)
            self.enviarAtualização()
            
    def verificaBufferMensagem(self) -> str:

        buffer = self.servidor.bufferMensagens
        
        if buffer != []:

            for enderecoDestinatario, mensagem in buffer:

                if enderecoDestinatario ==  self.clienteEndereco:  
                    
                    buffer.remove((enderecoDestinatario, mensagem))
                    self.mensagemProntaParaEnvio = mensagem + "\n"
                    
    def verificaBufferArquivo(self):
        
        buffer = self.servidor.bufferArquivos
        
        if buffer != []:

            for enderecoDestinatario, arquivo in buffer:

                if enderecoDestinatario ==  self.clienteEndereco:  
                    
                    buffer.remove((enderecoDestinatario, arquivo))
                    self.arquivoProntoParaEnvio = arquivo  

    def enviarArquivo(self, arquivo):
        
        arquivoTemporario = self.servidor.pathTemp + '/' + arquivo
        
        with open(arquivoTemporario, 'rb') as arquivo:
            self.clienteSocket.sendfile(arquivo, 0)
        
        os.remove(arquivoTemporario)
                                 
    def enviarAtualização(self):
        
        self.verificaBufferMensagem()
        
        self.verificaBufferArquivo()
        
        # cria o objeto
        objEnviar = servidor_para_cliente()
        
        # adiciona os usuarios
        objEnviar.usuariosAtivos = self.servidor.usuarios
        
        # adiciona as mensagens
        mensagem = self.mensagemProntaParaEnvio
        nomeArquivo = self.arquivoProntoParaEnvio
        
        objEnviar.mensagensRecebidas = mensagem
        objEnviar.nomeArquivo = nomeArquivo
        
        self.mensagemProntaParaEnvio = ''
        self.arquivoProntoParaEnvio = ''
        
        # serializa o objeto
        data_string = pickle.dumps(objEnviar)
        
        # envia o objeto serializado para o servidor
        self.clienteSocket.sendall(data_string)
        
        if mensagem != '':
            print(f"Mensagem enviada -> {self.clienteEndereco}:{mensagem}")
        if nomeArquivo != '':

            sleep(0.5)
            self.enviarArquivo(nomeArquivo)
            print(f"nomeArquivo enviado -> {self.clienteEndereco}:{nomeArquivo}")


class ThreadTela(threading.Thread):
    
    def __init__(self, servidor:Servidor):
        threading.Thread.__init__(self)
        self.servidor = servidor
        
    def run(self):
        self.servidor.tela = Tk()
        self.servidor.app = TelaServidor(self.servidor)
        self.servidor.tela.resizable(width=0, height=0)
        self.servidor.tela.mainloop()

if __name__ == '__main__':
    
    servidor = Servidor()
    