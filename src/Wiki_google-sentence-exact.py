#!/usr/bin/env python
# coding: utf-8

# ## Scrap Wikipédia
# 
# Langue étudiée: français

# ### Préparation d'environnement

# In[ ]:


import requests
import re
import os
import time
import pickle

from random import uniform
from tqdm import tqdm

# lib à installer
import pandas as pd
from bs4 import BeautifulSoup as bs
from nltk.tokenize import sent_tokenize, wordpunct_tokenize


# In[ ]:


#import nltk
#nltk.download('punkt')


# In[ ]:


def verify_rep(rep):
    '''
    Vérifier l'existence des répertoires, en créer si besoin
    '''
    try:
        os.makedirs(rep) # on essaie de créer le répertoire. si le répertoire existe déjà, cela renvoie une erreur
    except:
        pass # en cas d'erreur (le répertoire existe), on fait rien

def kw2name(kw):
    '''
    Formatage de variable
    '''
    return re.sub('\W', '_', kw.lower())


# In[ ]:


output_rep = '../0_data_google_exact'

verify_rep('../0_data_wiki/pages_aspirees')
verify_rep('../0_data_wiki/textes_bruts')
verify_rep(output_rep)


# ### Récupération de pages d'origine

# In[ ]:


def get_page(kw):
    '''
    Récupération des pages wikipédia
    
    input:
    kw (STR): nom de la page à récupérer
    
    output:
    kw (STR)
    page (STR): html de la page récupérée
    '''
    print('Loading Wikipedia page:', kw)
    
    global URL # l'url de l'api utilisé, défini dans l'environnement
    
    PARAMS = {
        "action": "parse", # l'api parse le contenu de la page et renvoie le text
        "page": kw, # on précise la page 
        "format": "json", # l'api renvoie le text en format json
        "prop":"text", # on ne prend que le text
        "section":0 # on ne prend que l'introduction (première section de la page)
    }
    
    S = requests.Session() # on crée une session avec requests
    R = S.get(url=URL, params=PARAMS) # on passe la requête à la session
    DATA = R.json() # on récupère le résultat au format json
    page = DATA["parse"]["text"]["*"] # on récupère la page html dans le json renvoyé
    
    filename = kw2name(kw)
    with open('../0_data_wiki/pages_aspirees/{}.html'.format(filename), 'w', encoding='utf8', newline='\n') as htmlfile:
        htmlfile.write(page) # on écrit la page html en local
        
    return kw, page


# ### Nettoyage de text

# In[ ]:


def span_filter(span):
    '''
    Fonction pour filtrer les balises span
    On ne veut pas de balise pour la transcription phonétique (span API) ni les messages d'erreur (span error)
    
    input:
    span (bs.tag): balise span
    
    output:
    bool
    '''
    try:
        return ('API' in span['class']) or ('error' in span['class'])
    except KeyError:
        print(span)
        return True

def get_text(p):
    '''
    Fonction pour nettoyer le html et extraire le texte de chaque paragraphe
    '''
    if p.sup:
        p.sup.extract()
    if p.span and span_filter(p.span): # enlever les span inutiles
        p.span.extract()
    if p.style:
        p.style.extract()
    text = p.text.strip() # enlever les espaces qui traînent
    text = re.sub('\s+', ' ', text) # enlever les suites d'espace produites lors du nettoyage
    if len(text) < 50: # enlever wikipédia machin "modifier - modifier page..."
        return ''
    else:
        return text

def parse_wiki_page(kw_page):
    '''
    Parsing de la page wikipédia
    Une balise p enveloppe un paragraphe. On parse toute l'arborescence html, on prend toutes les balises p, 
    et on nettoie ces balises pour obtenir une liste de texte brut.
    
    input:
    kw_page (TUPLE): (nom de page, html de page)
    page (STR): html de page
    
    output:
    text_list_net (LIST): liste de phrases
    '''
    
    kw, page = kw_page
    soup = bs(page, 'html5lib') # on parse la page
    p_list = soup.find_all('p') # on récupère toutes les p
    text_list = list(map(get_text, p_list)) # on nettoie les balises et on obtient les textes
    text_list_net = list(filter(lambda x: x, text_list)) # on enlève les textes vides
    
    # on filtre les phrases trop courtes 
    sent_list = []
    #_ = [sent_list.append(sent) for text in text_list_net for sent in sent_tokenize(text) if len(wordpunct_tokenize(sent)) > 10]
    for text in text_list_net:
        for sent in sent_tokenize(text):
            if len(wordpunct_tokenize(sent)) <= 13:
                print('Invalid sentence:', sent)
            if re.match('Erreur de référence', sent):
                print('Invalid sentence:', sent)
            else:
                sent_list.append(sent)
    
    filename = kw2name(kw)
    with open('../0_data_wiki/textes_bruts/{}.txt'.format(filename), 'w', encoding='utf8', newline='\n') as txtfile:
        txtfile.write('\n\n'.join(sent_list)) # on écrit ces textes en local
    
    return kw, sent_list


# ## Scrap Google

# In[ ]:


def sep_url(url):
    '''
    Nettoyage d'url
    '''
    if not url.startswith('http'): # des fois l'url aspiré commence par /url?p=, on coupe donc cette partie
        url = url[7:]
    url = re.split('&sa=', url)[0] # des morceaux inutiles traînent à la fin de l'url (anti-aspiration google), on les coupe avec regex
    if "%3" in url:
        url = re.split('%3', url)[0]
    return url

def net_url(url):
    if 'wikipedia' in url:
        return False
    elif 'google' in url:
        return False
    elif 'youtube' in url:
        return False
    else:
        return True

def get_url_list(quest, nb_url):
    '''
    Pour chaque phrase, on fait une requête google pour obtenir une liste d'url
    
    input:
    quest (STR): phrase à chercher
    nb_url (INT): nombre d'url à trouver
    
    output:
    url_net (LIST): liste d'url
    '''
    n = 0 
    url_list = []
    
    while n < nb_url:
        gap = uniform(1.0,10.0)
        time.sleep(gap)
        url = "http://www.google.fr/search?custom?hl=fr&q={}&start={}".format('\"{}\"'.format(quest), n)
        response = requests.get(url)
        data = response.text

        soup = bs(data, 'html.parser')
        div_main = soup.find('div', attrs={'id':'main'})
        divs = div_main.find_all('div', attrs={'class':'kCrYT'})
            
        url_list += [div.a['href'] for div in divs if div.a]
        url_short = list(map(sep_url, url_list))
        url_net = list(filter(net_url, url_short))
        
        n += 10
        
    return url_net

def url_to_name(url):
    if re.search('.*archives-ouvertes.*document', url):
        req_name = url.rsplit('/', maxsplit=2)[1]
        req_name += '.pdf'
    elif url.endswith('/'):
        req_name = url.rsplit('/', maxsplit=2)[1]
    else:
        req_name = url.rsplit('/', maxsplit=1)[1]
    if '.' not in req_name:
        req_name += '.html'
        
    if len(req_name) > 150:
        _ = req_name.split('.')
        req_name = '.'.join([_[0][:100] + _[1]])
        
    while not req_name[0].isalnum(): # *h.html
        req_name = req_name[1:]
    return req_name

def get_urls(texts, nb_url):
    '''
    Génération de bdd de nom_de_page - url_list
    
    input:
    texts (DICT): {nom_de_page: list(phrase1, phrase2...)}
    nb_url (INT): nombre d'url à récupérer
    
    output:
    url_dict (DICT): {nom_de_page: {phrase1:[url1, url2...]...}}
    '''
    global output_rep
    
    url_dict = {}
    
    for kw, text_list in texts.items(): # pour chaque paire nom_de_page - liste_de_paragraphes
        gap = uniform(1.0,10.0)
        print("{}: {} texts\nStarting in {}s...".format(kw, len(text_list), round(gap, 3)))
        time.sleep(gap)
        
        reppath = os.path.join(output_rep, kw2name(kw))
        verify_rep(reppath) # on crée un répertoire pour chaque nom de page
        
        excelname = 'urls.xlsx'
        excelpath = os.path.join(reppath, excelname)
        df_url = pd.DataFrame()
        df_stats = pd.DataFrame(index=['text', 'nb_url', 'longueur_text'])
        
        tmp = {}
        for i, text in enumerate(text_list): # pour chaque paragraphe
            url_list = get_url_list(text, nb_url) # on extrait la liste d'url 
            df_stats['sentence_{}'.format(i)] = [text, len(url_list), len(wordpunct_tokenize(text))]
            while len(url_list) < 51:
                url_list.append('')
            df_url['sentence_{}'.format(i)] = url_list
            
            
            tmp[text] = url_list
            filename = 'url_{}.txt'.format(i+1)
            filepath = os.path.join(reppath, filename)
            with open(filepath, 'w', encoding='utf8', newline='\n') as urlio:
                urlio.write('\n'.join(url_list)) # on écrit la liste en local
                
            # stocker le contenu des url en local
            url_rep = os.path.join(reppath, str(i+1))
            verify_rep(url_rep) # on crée le répertoire de sortie
            
            # fichier log pour chaque paragraphe
            log_path = os.path.join(reppath, 'log_{}.txt'.format(i+1))
            log_io = open(log_path, 'w', encoding='utf8', newline='\n') 
            
            # on lit chaque url
            for url in tqdm(url_list, total=len(url_list), desc="Processing text {}...".format(i+1)):
                try:
                    req = requests.get(url)
                except: # adresse non valide
                    log_io.write('Invalid url: {}\n\n'.format(url))
                    continue
                if req.status_code == 200: # connexion au serveur aboutie
                    req_name = url_to_name(url)
                    req_path = os.path.join(url_rep, req_name)
                    with open(req_path, 'wb') as req_io:
                        req_io.write(req.content)
                else: # connexion au serveur non aboutie
                    log_io.write('Invalid url: {}\n'.format(url))
                    log_io.write('Status code: {}\n\n'.format(req.status_code))
            
            log_io.close()
        
        with pd.ExcelWriter(excelpath) as writer:
            df_url.to_excel(writer, sheet_name='liste_url', encoding='utf8')
            df_stats.to_excel(writer, sheet_name='stats', encoding='utf8')

        pkl_path = os.path.join(reppath, '{}.pkl'.format(kw))
        with open(pkl_path, 'wb') as pkl_io:
            pickle.dump(tmp, pkl_io)
            
        url_dict[kw] = tmp
        
    return url_dict


# In[ ]:


URL = "https://fr.wikipedia.org/w/api.php" # l'api utilisé

KWS = [
    'Charles de Gaulle',
    'Pirates des Caraïbes : Jusqu\'au bout du monde',
    'À la recherche du temps perdu',
    'Alchimie',
    'Le Jour de Qingming au bord de la rivière'
]


url_dict = {}

pages = dict(map(get_page, KWS)) 
# on applique la fonction get_page à tous les éléments de KWS, le résultat est renvoyé sous forme de dictionnaire
# dictionnaire {nom_de_page:html_de_page}

print('\nParsing Wikipedia pages...\n')
texts = dict(map(parse_wiki_page, pages.items()))
# on applique la fonction parse_page à chaque item du dictionnaire pages, et on récupère le résultat sous forme de dictionnaire
# texts: {nom_de_page: list(paragraphe1, paragraphe2...)}

nb_url = 50
print('\n')
url_dict.update(get_urls(texts, nb_url))

