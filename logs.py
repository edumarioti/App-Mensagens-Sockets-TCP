from datetime import datetime
import os

def log(IpRementente, NomeRemetente, acao, IpDestinatarios='', NomeDestinatarios=''):

    data_agora = datetime.now()
    data = data_agora.strftime("%d-%m-%Y")
    hora = data_agora.strftime("%H:%M:%S")
       
    pathDoArquivo = str(os.path.dirname(os.path.realpath(__file__))) + "\\Logs"
    nomeDoArquivo = f"Log_{data}.txt"
    
    arquivoLog = os.path.join(pathDoArquivo, nomeDoArquivo)
    
    mensagemLog = f"{data} {hora} | {IpRementente} : {NomeRemetente} "
    
    if IpDestinatarios != '':
        mensagemLog += f"-> {IpDestinatarios} : {NomeDestinatarios} "
    
    mensagemLog += f"| {acao}\n"
    
    with open(arquivoLog,'a') as arquivo:
        arquivo.write( f"{mensagemLog}\n")
    
    return mensagemLog