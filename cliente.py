import pickle, socket
from time import sleep
from objetosCominicacao import *



class Cliente(object):
    
    def __init__(self):
        
        self.logado = False
        self.conectado = False
        self.usuario  = ''
        self.mensagem = ''
        self.acao     = ''

    def login(self, usuario:str):

        self.logado = True
        self.usuario = usuario
        self.enviar(acao=LOGIN)
          
    def logout(self):
        self.logado = False
        # Envia a informação de Logout
        self.enviar(acao=LOGOUT)
    
    def conectar(self):
        host = HOST
        port = PORT
        
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.connect((host,port))

        self.conectado = True
    
    def desconectar(self):
        self.conectado = False
        self.mySocket.close()
              
    def enviar(self, acao:str, mensagem='', destinatario=''):
        
        # cria o objeto
        objEnviar = cliente_para_servidor()
        objEnviar.remetente = str(self.usuario)
        objEnviar.acao = acao
        objEnviar.mensagem = mensagem
        objEnviar.destinatario = destinatario

        
        # serializa o objeto
        data_string = pickle.dumps(objEnviar)
        
        # envia o objeto serializado para o servidor
        self.mySocket.sendall(data_string)
    
    def enviarArquivo(self, pathArquivo):
        
        with open(pathArquivo, 'rb') as arquivo:
            self.mySocket.sendfile(arquivo, 0)
        
        
    def verificarRespostaServidor(self):
        
        if self.conectado:
            
            dados = self.mySocket.recv(4096)
            
            if dados != b'':
                #desserializa a mensagem recebida, disponibilizando o objeto novamente na memoria
                objetoRecebido:servidor_para_cliente
                objetoRecebido = pickle.loads(dados)
                
                return objetoRecebido     
                
        return None
