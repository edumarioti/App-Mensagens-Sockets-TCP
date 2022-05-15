
HOST = '127.0.0.1'
PORT = 10000

LOGIN = 'IN'
LOGOUT = 'OUT'
MENSAGEM = 'MSG'
ARQUIVO = 'ARQ'
RECEBER_ARQUIVO = 'RECVARQ'

class cliente_para_servidor(object):
    
    def __init__(self):
       
        self.remetente    = ''
        self.acao         = ''
        self.mensagem     = ''
        self.destinatario = ''



class servidor_para_cliente(object):
    
    def __init__(self):
        
        self.usuariosAtivos     = []
        self.mensagensRecebidas = ''
        self.arquivo            = ''
        
