# PFE_M2
Ceci est le répertoire git du projet de fin d'étude M2 TAL DEFI. <br><br>

## Plan de l'arborescence
    - ./src: scripts (.ipynb & .py) de scrapping wikipédia et google <br>
    - ./0_data_wiki: (DEPRECATED) exemple de sortie du scrapping wikipédia avec "Charles de Gaulle" et "Amélie Nothomb" <br>
    - ./0_data_google: (DEPRECATED) exemple de sortie du scrapping google avec "Charles de Gaulle" et "Amélie Nothomb" <br>
    - ./1_annotations: deux fichiers pour chaque mot clé: stats.xlsx avec les annotations manuelles brutes, .pkl avec les données binaires de correspondance phrase-urls google <br>
    - ./1_annotations_net: trois fichiers pour chaque mot clé: stats.xlsx avec les annotations uniformisées et centralisées, urls.xlsx avec les annotations redistribuées aux urls de chaque phrase, .pkl avec les données binaires de correspondance phrase-urls google <br>
    - ./1_statistiques: les analyses statistiques effectuées sur l'ensemble de données
    

## Utilisation de script
Librairies à installer: bs4, nltk, pandas==1.0.1<br><br>

Les .py sont produits en convertissant directement les .ipynb. Le format du code ne sont donc pas forcément adapté. Ils n'acceptent pas de paramètres par ligne de commande. Les modifications des paramètres se font directement dans le script. <br><br>

Les deux scripts correspondent aux deux types de requêtes utilisées dans l'étude. Ils fonctionnement de la même manière, la seule différence consiste dans les requêtes passées à Google. <br><br>

**Entrée**<br>
Deux paramètres sont obligatoires: `KWS` une liste de mots clés, `nb_url` le nombre d'urls à trouver par phrase. <br><br>

**Sortie**<br>
Trois fichiers en sortie pour chaque mot clé: stats.xlsx avec les urls de toutes les phrases, centralisées et triées par nombre d'occurrences, urls.xlsx avec les urls correspondants à chaque phrase, .pkl avec les données binaires de correspondance phrase-urls google.
