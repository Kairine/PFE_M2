#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import pandas as pd

from collections import Counter


# ### pkl to stats

# In[99]:


def pkl_to_stats(output_rep):

    for name in os.listdir(output_rep):
        corpus_path = os.path.join(output_rep, name)
        print('Processing', corpus_path)
        if '{}_stats.xlsx'.format(name) not in os.listdir(corpus_path): # pour garder les résultats déjà faits
            
            # charger les données pkl
            datapath = os.path.join(corpus_path, '{}.pkl'.format(name))
            with open(datapath, 'rb') as pklio:
                data = pickle.load(pklio)

            # compter le nombre d'occurrences
            c = Counter()
            _ = [c.update(urls) for urls in data.values()]
            del c['']

            # counter to df
            c_ = c.most_common()
            df_counts = pd.DataFrame(columns=['url', 'nb_occur', 'copier_coller', 'degré_cc', 'longueur', 'type', 'domaine', 'citer_source', 'licence', 'misc'])
            df_counts = df_counts.assign(url=[p[0] for p in c_])
            df_counts = df_counts.assign(nb_occur=[p[1] for p in c_])

            # df to excel
            statpath = os.path.join(corpus_path, '{}_stats.xlsx'.format(name))
            with pd.ExcelWriter(statpath) as writer:
                df_counts.to_excel(writer, sheet_name='comptage_url', encoding='utf8')
                
    return True

if __name__ == '__main__':
    pkl_to_stats('../0_data_google')
    pkl_to_stats('../0_data_google_exact')

