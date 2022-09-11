

'''
Semplice bot di Telegram\companion app del gioco di carte Magic The Gathering con comandi basilari e conversazione
'''

#Librerie: telebot-interfaccia con telegram, datetime- data e ora dello scraping
# re -regex per il matching della conversazione, np - randomizzazione risposte

#bot creato con BotFather e chiamato RickyMagicBot

import telebot
import datetime
import re
import numpy as np

API_TOKEN = '5225131770:AAEoVhedDNiE_gCIGcufieZ4CQBU7IQTgFE'

bot = telebot.TeleBot(API_TOKEN)

# definizione del comando '\start'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """\
    Ciao, sono MagicBot, la tua risorsa sulle carte collezionabili Magic The Gathering. Come posso aiutarti?\
    """)

# definizione del comando '\help'

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """\
Vedo che hai bisogno ti aiuto! adesso ti illustro tutto ciò che so fare:\n

/start                   Ti darò il benvenuto nella mia chat\n
/help                    Ti aiuterò come posso\n
/price                   Ti dirò il prezzo di odierno di una carta\n

Puoi anche parlarmi o chiedermi consigli sui mazzi, ti risponderò come posso!          
                 """)

# definizione del comando '\price', che daraà inizio alla sequenza di scraping dei prezzi

@bot.message_handler(commands=['price'])
def card_asking(message):
    ask = bot.send_message(message.chat.id, "Scrivi il nome di una carta e ti dirò il prezzo di oggi. Mi raccomando, scrivilo correttamente!")
    bot.register_next_step_handler(ask, card_price)
    
#funzione di web scraping per la ricerca del prezzo delle carte usando il sito Cardmarket.com,
#piattaforma di vendita attendibile e multilingua che permette di vedere i prezzi reali dei prodotti

def card_price(message):
    import urllib.request
    from bs4 import BeautifulSoup 
    
    #la lista facilita la conservazione e la correttezza dell'output
    #in fase di test si è dimostrata più affidabile e capace di scremare input errati
    
    price=[]
    
    #ricerca della carta nel database, impostata su 'cerca nome esatto'
    #pulizia dell'input per facilitare la scrittura dell'Url, poichè mantenendo i caratteri speciali la ricerca fallisce
    #così facendo occorre solamente digitare correttamente la parte letterale dei nomi delle carte
    # es. input = Urza's Saga ---> search = urzassaga
    
    
    raw_input = message.text
    clean_input  = raw_input.lower().replace(" ","").replace("'","").replace(",","").replace(".","")
    
    #determinazione della data della ricerca, per poter contestualizzare il prezzo trovato
    
    current_date = datetime.datetime.now().strftime('%d-%m-%Y')
    
    #compilazione Url e lettura con bs4

    response= urllib.request.urlopen('https://www.cardmarket.com/it/Magic/Products/Search?idCategory=0&idExpansion=0&searchString=%5B'+ str(clean_input) +'%5D&exactMatch=on&idRarity=0&perSite=30')
    html= response.read()
    soup= BeautifulSoup(html,'html5lib')
    
    #limitare la ricerca degli elementi al body della pg web
    # per escludere elementi di disturbo o prezzi di altri elementi

    all_price=soup.find_all('div',{'class':"table-body"})
    
    # immagazzinamento dei prezzi trovati nel body attraverso la classe corrispondente
    # verrà inviato solo il primo, ovvero il prezzo della carta base (escludendo quindi le edizioni speciali)
    
    for i in range(len(all_price)):
        price.append(all_price[i].find('div',{'class':"col-price pr-sm-2"}).text)
    
    
    # tentativo di invio del prezzo
    # se avviene un errore, quasi certamente il nome errato della carta, invia un messaggio

    try:
        bot.send_message(message.chat.id, 'Il prezzo medio è ' + (price[0]) + '\n' + 'al ' + current_date)
    except:
       bot.send_message(message.chat.id, "Hai sbagliato qualcosa, ricontrolla il nome della carta" )
       pass

# gestione messaggi con componente testuale, usiamo le regex per matchare gli imput testuali dell'utente
# facilitiamo il matching con dei flags (in questo caso IGNORECASE)
# usiamo la funzione re.search (le regex normali funzionano male, probabilmente a causa della natura end2end di Telegram)

@bot.message_handler(func=lambda message: True)
def response_chat(message):
    if re.search(r'consigli|suggeri', message.text, flags= re.IGNORECASE):
        
         #risp casuale a  consigli sui mazzi del gioco
    
        deck_list = ["Monoverde aggro in Standard", "Izzet Murktide in Modern", "Golgari control in Standard", "Izzet Phoenix in Historic", "Death&Taxes in Legacy", 
                     "Mononero in Standard", "Naya aggro in Standard", "Grixis affinity in Pauper", "Izzet Turni in Standard", "Golgari sacrifice in Standard", "Gattoforno in Historic"]
        deck_exp_list = ["Ti consiglio ","A me piace molto ", "Mi sto divertendo tanto con ", "Sto vincendo tante sfide con ", "Ultimamente fa ottimi risultati "]
        response_deck = str(*np.random.choice(deck_exp_list, 1)) + str(*np.random.choice(deck_list, 1))
        bot.reply_to(message, response_deck)
    
    #risp al saluto
    
    elif re.search(r'ciao|hey|hola|buongiorno|buon giorno|buonasera|buona sera',message.text, flags= re.IGNORECASE):
    
        #risp variabile a seconda dell'ora del giorno, usiamo l'ora attuale per distinguere notte e giorno
        
        import time
        
        mytime = time.localtime()
        
        if mytime.tm_hour < 6 or mytime.tm_hour > 18:
            bot.reply_to(message, "Ciao a te, oggi è una bella serata per giocare a Magic The Gathering!")
        else:
            bot.reply_to(message, "Ciao a te, oggi è una bella giornata per giocare a Magic The Gathering!")
    
    #risp casuale a 'come stai?'
    
    elif re.search(r'come', message.text, flags= re.IGNORECASE) and re.search(r'stai|ti senti|butta',message.text, flags= re.IGNORECASE):
        bot.reply_to(message, "Sto benissimo! Sto giocando a Magic The Gathering!")
        
    #risp casuale a preferenza colore carte
    
    elif re.search(r'qual|che', message.text, flags= re.IGNORECASE) and re.search(r'color',message.text, flags= re.IGNORECASE):
        
        color_list = ["il verde", "il nero", "il bianco", "il rosso", "il blu", "incolore artefatti"]
        color_exp_list = ["Ovviamente ","Sicuramente ", "Non può essere altro che ", "Che domande, "]
        
        response_color = str(*np.random.choice(color_exp_list, 1)) + str(*np.random.choice(color_list, 1)) + "!"
        bot.reply_to(message, response_color)
    
    #risp casuale a preferenza combinazione colori
    
    elif re.search(r'qual|che', message.text, flags= re.IGNORECASE) and re.search(r'gilda|combinazione',message.text, flags= re.IGNORECASE):
        
        guild_list = ["Orzhov", "Dimir", "Selesnya", "Golgari", "Izzet", "Grixis", "Sultai", "Esper"]
        guild_exp_list = [" senza dubbio",", e quale se no", " è la risposta ovvia", ""]
        
        response_guild = str(*np.random.choice(guild_list, 1)) + str(*np.random.choice(guild_exp_list, 1)) + "!"
        bot.reply_to(message, response_guild)
                            
    else:
        bot.reply_to(message, 'Scusami, ma non ho capito')


bot.polling()
