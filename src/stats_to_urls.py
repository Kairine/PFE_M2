#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import pandas as pd

from collections import Counter


# ### stats to urls

# In[66]:


def stats_to_urls(output_rep):
    for name in os.listdir(output_rep):
        corpus_path = os.path.join(output_rep, name)
        urls_path = os.path.join(corpus_path, '{}_urls.xlsx'.format(name))
        stats_path = os.path.join(corpus_path, '{}_stats.xslx'.format(name))
        data_path = os.path.join(corpus_path, '{}.pkl'.format(name))
        
        with open(data_path, 'rb') as pklio:
            data = pickle.load(pklio)
        
        res = pd.read_excel(stats_path, index_col=0)
        res = res.set_index('url')

        with pd.ExcelWriter(urls_path) as writer:
            for i, item in enumerate(data.items()):
                sent, urls_list = item
                df = pd.DataFrame(columns=res.columns)
                for url in urls_list:
                    if url:
                        df = df.append(res.loc[url, :])
                df = df.reset_index().rename(columns={'index':'url'})
                df.to_excel(writer, sheet_name='text_{}'.format(i+1))
                #print(sent)
                
    return True


# In[ ]:

if __name__ == '__main__':
    stats_to_urls('../0_data_google')
    stats_to_urls('../0_data_google_exact')


