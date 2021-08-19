import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox as msgbox
import socket
from time import sleep
import threading
import random as rnd

#FINESTRA DI GIOCO PRINCIPALE
window_main = tk.Tk()
window_main.title("Game Chat")
name = ""
player_class = ""
game_round =300 #Tempo di gioco(5 minuti)
game_timer = 4
choice = ""
score = 0
#Client di rete
client = None
HOST_ADDR = ''
HOST_PORT = 60000
door_sample=rnd.sample(range(3), 3)
question=[]
correct_answer = ""
txtCountDown = "" #Variabile usata per il controllo sul sul timer di gioco


def game_logic(arg):
   global choice, client, game_round, score, correct_answer
   enable_disable_answers("disable")
   if arg==correct_answer:
       lbl_answers["text"]="Risposta corretta, +1 punto"
       score+=1
   else:
       lbl_answers["text"]="Risposta errata, -1 punto"
       score-=1
   sleep(1)
   lbl_result["text"]=score
   if score==0:
       lbl_result["foreground"]="grey"
   elif score >0:
       lbl_result["foreground"]="green"
   else:
       lbl_result["foreground"]="red"

   doorShuffler()
   enable_disable_doors("enable")
   
   


def enable_disable_doors(cond):
    if cond == "disable":
        btn_door1.config(state=tk.DISABLED)
        btn_door2.config(state=tk.DISABLED)
        btn_door3.config(state=tk.DISABLED)
    else:
        btn_door1.config(state=tk.NORMAL)
        btn_door2.config(state=tk.NORMAL)
        btn_door3.config(state=tk.NORMAL)

def enable_disable_answers(cond):
    if cond == "disable":
        btn_Scelta_1.config(state=tk.DISABLED)
        btn_Scelta_2.config(state=tk.DISABLED)
    else:
        btn_Scelta_1.config(state=tk.NORMAL)
        btn_Scelta_2.config(state=tk.NORMAL)

def enable_frame_question():
    lbl_questioID.pack()
    lbl_question.pack()
    lbl_answers.pack()

def doorShuffler():#Mescola le tre porte
    door_sample=[]
    door_sample=rnd.sample(range(3),3)


def connect():
    global name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="Devi inserire un nome <e.g. John>")    
    elif len(ent_ip_Addr.get()) < 8:
        tk.messagebox.showerror(title="ERROR!!!", message="Devi inserire un indirizzo ip valido <e.g. 255.255.255.255>")   
    else:
        name = ent_name.get()
        lbl_your_name["text"] = "Il tuo nome: " + name
        connect_to_server(name)

def exit_game():
    global client,name
    msgbox.showerror(title="Partita finita", message="Giocatore:" + name + ", Classe:" + player_class+", ha ottenuto:" + str(score) + " punti\n")
    client.send(bytes("$quit", "utf-8"))
    client.close()
    window_main.destroy()

def count_down(my_timer, nothing): #Tempo prima di inizio possibilità di giocare
    lbl_game_round["text"] = "Il gioco inizia in"

    while my_timer > 0:
        my_timer -= 1
        print("Tempo di gioco è: " + str(my_timer))
        lbl_timer["text"] = my_timer
        sleep(1)

    enable_disable_doors("enable")

def game_count_down(my_timer, nothing):#Durata di gioco
    global game_round
    lbl_game_round["text"] = "Tempo rimanente:"
    var=game_round
    low_lim=var*0.25
    while var > 0:
        var -= 1
        lbl_timer["text"] = var
        if(var < low_lim):#Il tempo diventa rosso quando è vicino allo scadere
            lbl_timer["foreground"]="red"
        sleep(1)

    lbl_timer["text"] = "Tempo scaduto!"
    enable_disable_doors("disable")
    enable_disable_answers("disable")
    exit_game()



def door_choice(arg):
    global choice, client, score,player_class,name,question
    enable_disable_doors("enable")
    door_types={
        0:"Domanda",
        1:"Domanda",
        2:"Trappola"
    }
    if client:
        lbl_door_choice["text"]="La porta scelta è la numero:"+ str(arg)+" e incontri una: "#+ door_types.get(arg,"Invalid choice")
        if arg==2:
            lbl_selected_door["text"]="Trappola"#Semplice piccolo effetto grafico
            lbl_selected_door["foreground"]="red"
            exit_game()#Scegliendo la porta trapppola il gioco finisce
        else:
            lbl_selected_door["text"]="Domanda"
            lbl_selected_door["foreground"]="green"
            client.send(bytes("$domanda", "utf-8"))
        client.send(bytes(choice, "utf8")) #Il server invia la scelta della porta al server
        print(question)
        enable_disable_doors("disable")
        enable_disable_answers("enable")
    doorShuffler()
        

def enable_disable_ent_ip_Addr(cond):
    if cond == "disable":
        ent_ip_Addr.config(state=tk.DISABLED)        
    else:
        ent_ip_Addr.config(state=tk.NORMAL)       

def connect_to_server(name1):
    global client, HOST_PORT, HOST_ADDR, name
    try:
        HOST_ADDR=str(ent_ip_Addr.get())#Ottengo l'ip del host  
        enable_disable_ent_ip_Addr("disable")     
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name1.encode()) # Invia il nome al server dopo la connessione
        # disable widgets
        btn_connect.config(state=tk.DISABLED)
        btn_quit.config(state=tk.NORMAL)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)
        enable_disable_doors("disable")
        enable_disable_answers("disable")

        # avvia un thread per continuare a ricevere messaggi dal server
        # non bloccare il thread principale
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")
        enable_disable_ent_ip_Addr("enable")  
        print(e)

def receive_message_from_server(sck, m):
    global name,choice,score,player_class,correct_answer,txtCountDown

    while True:
        try:#Semplice protezione(in caso di tempo scaduto per esempio darebbe una eccezione)
         from_server = sck.recv(4096)
        except:
            break

        if not from_server: break
         
        if txtCountDown=="":
            threading._start_new_thread(count_down, (game_timer, ""))

        if from_server.startswith("z".encode()):#Inizio del gioco una volta loggato
            player_class=from_server.decode("utf-8")#Ottengo il ruolo dal server
            player_class=player_class[1:]#Genero il ruolo senza carattere di riconoscimento
            
            #Attivo una parte di grafica
            top_frame.pack()
            middle_frame.pack()
            lbl_welcome["text"] = "Salve " + name + "! Il tuo ruolo sara' " + player_class + ". Ora scegli una porta"
            lbl_your_name["text"] = "PC:" + name + "\n~" + player_class

            lbl_welcome.config(state=tk.DISABLED)
            lbl_line_server.config(state=tk.DISABLED)

            sleep(game_timer)
            txtCountDown="#La uso come stringa di controllo fermando il count down per l'inizio del gioco"
            
            #generazione timer di gioco
            th_timer=threading.Thread(target=game_count_down, args=(game_round, ""))#Creo il thread che farà da timer
            th_timer.daemon = True  #Il thread viene fatto girare in background in modo da lasciare che il gioco prosegua
            th_timer.start()

        elif from_server.startswith("-".encode()):#Inizio per le domande
            print("-domanda ricevuta\n")
            global correct_answer
            config_domanda_server=from_server.decode("utf-8")#Ricevo la stringa con la domanda formattata
            question=config_domanda_server.split('-')#Splitto la domanda in ['id', 'domanda', 'risposte', 'risposta esatta'] 
            print(config_domanda_server)
            print(question)
            correct_answer=question[4]#salvo la risposta esatta per poter fare poi il confronto con la risposta dell'utente

            #genero la grafica con le domande
            lbl_questioID["text"] = "Domanda n°" + question[1]   #id della domanda, parto da [1] perchè nella posizione [0] ho uno spazio vuoto
            lbl_question["text"]  = question[2]                  #corpo della domanda
            lbl_answers["text"]   = question[3]                  #risposte per l'utente
            enable_disable_answers("enable")    #attivo le risposte
            enable_frame_question()             #attivo la grafica delle domande
    sck.close()

###############################################################Parte Grafica######################################################################################################
top_welcome_frame= tk.Frame(window_main)

new_host_frame=tk.Frame(top_welcome_frame)
lbl_name = tk.Label(new_host_frame, text = "Nome:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(new_host_frame)
ent_name.pack(side=tk.LEFT)
new_host_frame.pack(side=tk.TOP)

new_ip_frame=tk.Frame(top_welcome_frame)
lbl_name = tk.Label(new_ip_frame, text = "Inserisci server ip:")
lbl_name.pack(side=tk.LEFT)
ent_ip_Addr = tk.Entry(new_ip_frame)
ent_ip_Addr.pack(side=tk.LEFT)
new_ip_frame.pack(side=tk.BOTTOM)

button_connection_frame=tk.Frame(top_welcome_frame)
btn_connect = tk.Button(button_connection_frame, text="Connect", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
btn_quit = tk.Button(button_connection_frame, text="Quit", command=lambda : exit_game(), state=tk.DISABLED)
btn_quit.pack(side=tk.LEFT)
button_connection_frame.pack(side=tk.BOTTOM)

top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="----------------------------------------------------------").pack()
lbl_welcome = tk.Label(top_message_frame, text="")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="-------------------------------------------------------")
lbl_line_server.pack_forget()
top_message_frame.pack(side=tk.TOP)


top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text="Your name: " + name, font = "Helvetica 13 bold")
lbl_player_class = tk.Label(top_left_frame, text="Class: " + player_class)
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
lbl_player_class.grid(row=1, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_game_round = tk.Label(top_right_frame, text="Game round (x) starts in", foreground="black", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text=" ", font = "Helvetica 24 bold", foreground="green")
lbl_game_round.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="-------------------------------------------------------------------").pack()
lbl_line = tk.Label(middle_frame, text="|--- SELEZIONA UNA TRA LE TRE PORTE ---|", font = "Helvetica 13 bold", foreground="blue").pack()
lbl_line = tk.Label(middle_frame, text="-------------------------------------------------------------------").pack()

round_frame = tk.Frame(middle_frame)
lbl_round = tk.Label(round_frame, text="Round")
lbl_round.pack()

#gestione door
lbl_door_choice = tk.Label(round_frame, text="La tua scelta: " + choice, font = "Helvetica 13 bold")
lbl_door_choice.pack()
lbl_selected_door = tk.Label(round_frame,text="porta", font = "Helvetica 13 bold")
lbl_selected_door.pack()

button_frame_2 = tk.Frame(middle_frame)
btn_Scelta_1 = tk.Button(button_frame_2, text="Risposta 1", command=lambda : game_logic("1"), state=tk.DISABLED)
btn_Scelta_2 = tk.Button(button_frame_2, text="Risposta 2", command=lambda : game_logic("2"), state=tk.DISABLED)
btn_Scelta_1.grid(row=0, column=0)
btn_Scelta_2.grid(row=0, column=3)
button_frame_2.pack(side=tk.BOTTOM)

lbl_result_text = tk.Label(round_frame, text="Punti ottenuti: ", foreground="blue", font = "Helvetica 14 bold")
lbl_result_text.pack()
lbl_result = tk.Label(round_frame, text=" 0", foreground="blue", font = "Helvetica 14 bold")
lbl_result.pack()
round_frame.pack(side=tk.TOP)



#Frame generazione domanda
last_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(last_frame, text="***********************************************************").pack()
lbl_questioID = tk.Label(last_frame, text="_", font = "Helvetica 10 bold")
lbl_questioID.pack()
lbl_question = tk.Label(last_frame, text="_", font = "Helvetica 10 bold")
lbl_question.pack()
lbl_answers = tk.Label(last_frame, text="_", font = "Helvetica 10 bold")
lbl_answers.pack()
lbl_line = tk.Label(last_frame, text="***********************************************************").pack()
last_frame.pack(side=tk.TOP)  

middle_frame.pack_forget()

#Frame bottoni con porte
button_frame = tk.Frame(window_main)
photo_wooden_door = PhotoImage(file="door.png")

btn_door1 = tk.Button(button_frame, text="Door 1", command=lambda: door_choice(door_sample[0]), state=tk.DISABLED, image=photo_wooden_door)
btn_door2 = tk.Button(button_frame, text="Door 2", command=lambda: door_choice(door_sample[1]), state=tk.DISABLED, image=photo_wooden_door)
btn_door3 = tk.Button(button_frame, text="Door 3", command=lambda: door_choice(door_sample[2]), state=tk.DISABLED, image=photo_wooden_door)

btn_door1.grid(row=0, column=0)
btn_door2.grid(row=0, column=1)
btn_door3.grid(row=0, column=2)
button_frame.pack(side=tk.BOTTOM)

window_main.mainloop()