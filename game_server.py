#Importo i moduli che utilizzo
import tkinter as tk
import socket
import threading
from time import sleep
import random as rnd


window = tk.Tk()
window.title("Game Server")
server = None
HOST_ADDR = ''
HOST_PORT = 60000
client_name = " "
clients = []
clients_names = []
player_data = []

def get_server_ip():#Funzione usata per ottenere l'ip del server che il client userà per connettersi
    global HOST_ADDR
    hostname=socket.gethostname()
    x=socket.gethostbyname(hostname)
    return(x)


def class_generator(): #Generatore una classe per un giocatore
    Class=rnd.randrange(1,10,1)
    classes={
        1: "Barbaro",
        2: "Mago",
        3: "Druido",
        4: "Paladino",
        5: "Guerriero",
        6: "Bardo",
        7: "Ladro",
        8: "Assassino",
        9: "Monaco",
        10: "Chierico"
    }
    return classes.get(Class,"Invalid Class Number")

def question_generator(): #Generatore una domanda per un giocatore
    question=rnd.randint(1, 15)#Dimensione limitata in quanto si tratta solo di un test
    question_list={
        1: "1-Nel videogioco Witcher 3 qual'è il nome del re della caccia selvaggia?-A)Lambert . B)Eredin-2",
        2: "2-Nella serie tv yugioh duel monsters qual'è il nome del faraone?-A)Akamon . B)Atem-2",
        3: "3-Nella serie tv battle spirits qual'è il colore del mazzo del rivale del protagonista?-A)Bianco . B)Blu-1",
        4: "4-Nella serie tv battle spirits qual'è il colore del mazzo dell'antagonista principale?-A)Rosso . B)Nero-1",
        5: "5-Quale pokemon ha la più bassa somma totale delle proprie statistiche?-A)Magikarp . B)Sunkern-2",
        6: "6-Qual'è il nome del ragazzo assistente del personaggio di fantasia professor Layton?-A)Mark . B)Luke-2",
        7: "7-Nel videogioco bloodborne quale arma è considerata la più potente?-A)La spada sacra di ludwig . B)Le lame della pietà-1",
        8: "8-Nel videogioco bloodborne quale boss è considerato il più difficile?-A)Laurence il primo vicario . B)Orfano di kos-2",
        9: "9-Nel videogioco dark souls 3 qual'è il boss finale del gioco di base?-A)Anima di tizzoni . B)Sorella Friede & Padre Ariandel-1",
        10: "10-Nei videogiochi pokemon HeartGold and SoulSilver chi è il campione della lega?-A)Il tuo rivale . B)Lance-2",
        11: "11-Nel videogioco Terraria quale boss è considerato il più debole?-A)Golem . B)Re slime-2",
        12: "12-Nella serie tv Power Rangers quale ranger è generalmente il leader?-A)Ranger Bianco . B)Ranger Rosso-2",
        13: "13-Nella serie tv I Simson qual'è il nome del figlio di Homer?-A)Nelson . B)Bart-2",
        14: "14-Nel videogioco Witcher 3 qual'è il nome del personaggio che il giocatore controlla?-A)Vesemir . B)Geralt-2",
        15: "15-Nel videogioco Hollow Knight chi è il vero boss finale?-A)The Radiance . B)The Hollow Knight-1"
    }
    return question_list.get(question,"Invalid Question Number")


def get_ip_addr():
   #Ottengo l'ip e lo mostro a video
    x = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        x.connect(('10.255.255.255', 1))
        Ind_Ip = x.getsockname()[0]
    except:
        Ind_Ip = '127.0.0.1'
    finally:
        x.close()
    return Ind_Ip

#Avvia la funzione server
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print (socket.AF_INET)
    print (socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  #Il server è in ascolto per la connessione del client

    threading._start_new_thread(accept_clients, (server, " "))

    print("Server Started")


#Arresta la funzione server
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:       
            client, addr = the_server.accept()
            clients.append(client)
            #Utilizza un thread in modo da non intasare il thread della gui
            threading._start_new_thread(send_receive_client_message, (client, addr))

#Funzione per ricevere messaggi dal client corrente E
#Invia quel messaggio agli altri client
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, index

    index = get_client_index(clients,client_connection)
    client_name = client_connection.recv(4096)

    client_class = class_generator()#Genera la classe
    client_connection.send(bytes("z"+client_class, "utf8"))
    clients_names.append(client_name)
    update_client_names_display(clients_names)  #Aggiornare la visualizzazione dei nomi dei client
    sleep(1)

    while True:
        data = client_connection.recv(4096)
        if not data: break

        #Estrae la scelta del giocatore dai dati ricevuti
        player_choice = data[11:len(data)]
        msg = {
            "choice": player_choice,
            "socket": client_connection
        }
        player_data.append(msg)

        if(player_choice == "$quit"):
            client_connection.send(bytes("!Sei caduto nella mia trappola", "utf8"))
            #Trova l'indice del client, quindi lo rimuove dagli elenchi del client e quello delle connessioni
            del clients[index]
            del clients_names[index]           
            client_connection.close()
            update_client_names_display(clients_names) #Aggiorna la visualizzazione dei nomi dei client
        else:
            print("Richiesta di una domanda\n")
            question_config="-"+question_generator()
            print(question_config)
            try:#protezione
                client_connection.send(bytes(question_config, "utf8"))
            except:
                break



#Restituisce l'indice del client corrente nell'elenco dei client
def get_client_index(client_list, curr_client):
    indice = 0
    for conn in client_list:
        if conn == curr_client:
            break
        indice += 1

    return indice


# Aggiorna la visualizzazione del nome del client quando un nuovo client si connette O
# Quando un client connesso si disconnette
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c.decode() + "\n")
    tkDisplay.config(state=tk.DISABLED)

#Cornice superiore composta dai pulsanti btnStart e btnStop
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

#Cornice centrale composta da due etichette per la visualizzazione delle informazioni sull'host e sulla porta
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address:"+str(get_ip_addr()))
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:"+ str(HOST_PORT))
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

#Il frame client mostra l'area dove sono elencati i clients che partecipano al gioco
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="___________Gamers List___________").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

window.mainloop()