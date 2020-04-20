# PFE_M2
Ceci est le répertoire git du projet de fin d'étude M2 TAL DEFI. <br><br>
Plan de l'arborescence: <br>
    - ./src: scripts (.ipynb & .py) de scrapping wikipédia et google <br>
    - ./0_data_wiki: exemple de sortie du scrapping wikipédia avec "Charles de Gaulle" et "Amélie Nothomb" <br>
    - ./0_data_google: exemple de sortie du scrapping google avec "Charles de Gaulle" et "Amélie Nothomb" <br>

**Description de script:** <br>
Librairies à installer: bs4, nltk<br><br>

Le script accepte `KWS` une liste de mots clés et `nb_url` un nombre d'url à trouver par paragraphe. 
En sortie, chaque paragraphe de chaque page Wikipédia aura un txt pour stocker les url, un fichier log pour enrigistrer les url non valides et un répertoire avec les fichiers googlés dedans. 
