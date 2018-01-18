
# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath('../CaseLawAnalytics/'))
sys.path.insert(0, os.path.abspath('..'))


# In[2]:


from lxml import etree
from caselawres import dbutils
from caselawnet.lido_parser import LinkExtractorXMLParser, LinkExtractorRDFParser

# In[3]:

## Settings
fp = '/media/sf_VBox_Shared/CaseLaw/lido_rdf/2017-11-28-xml/'



conn = dbutils.get_connection()  


# In[71]:

conn.execute(''' DROP TABLE IF EXISTS uitspraken_meta''')
conn.execute(''' CREATE TABLE uitspraken_meta
            (id text PRIMARY KEY, 
            title text,
            summary text,
            updated text
            )
        ''')


# ## Retrieve all HR meta data

# In[61]:

def get_entries_from_link(baselink, fr=0,                           maximum=1000):
    link = baselink+'&max='+str(maximum)+'&from='+str(fr)
    xml_element = etree.ElementTree().parse(link)
    entries = list(xml_element.iter('{*}entry'))
    return entries


# In[62]:


def get_first_content(el, tag):
    return list(el.iter('{*}'+tag))[0].text

def insert_into_uitspraken_meta(entry, curs, table='uitspraken_meta'):
    id0 = get_first_content(entry, 'id')
    title = get_first_content(entry, 'title')
    summary = get_first_content(entry, 'summary')
    updated = get_first_content(entry, 'updated')
    
    query = ''' INSERT OR REPLACE INTO uitspraken_meta
        VALUES (?, ?, ?, ?)
    '''
    curs.execute(query, (id0, title, summary, updated))


# In[72]:

baselink = 'http://data.rechtspraak.nl/uitspraken/zoeken?' + \
           'creator=http://standaarden.overheid.nl/owms/terms/Hoge_Raad_der_Nederlanden' +\
           '&type=Uitspraak'

# In[73]:

size = 1000
end = 98000
for start in range(0, end, size):
    entries = get_entries_from_link(baselink, start, size)
    print(start, len(entries))
    for entry in entries:
        insert_into_uitspraken_meta(entry, conn)


# In[75]:

conn.commit()


# ## Download RDFs from LiDO

# In[86]:




# In[99]:

filename = 'settings.cfg'
with open(filename) as f:
    exec(compile(f.read(), filename, 'exec'))

rdf = False
if rdf:
    LinkExtractorRDFParser(auth = {'username': LIDO_USERNAME, 'password':LIDO_PASSWD})
else:
    parser = LinkExtractorXMLParser(auth = {'username': LIDO_USERNAME, 'password':LIDO_PASSWD})


# In[106]:



failed_eclis = []

i = 0
for (ecli,) in conn.execute('select id from uitspraken_meta'):
    if i%1000 == 0:
        print(i)
    ext = '.rdf' if rdf else '.xml'
    fn = ecli.replace(':', '_') + ext
    if not os.path.exists(os.path.join(fp, fn)):
        lido_id = parser.get_lido_id(ecli)
        if rdf:
            url = "{}?id={}".format(parser.LIDO_API_URL, lido_id)
        else:
            url = "{}?id={}&output=xml".format(parser.LIDO_API_URL, lido_id)

        try:
            response = parser.get_lido_response(url)
            
            with open(os.path.join(fp, fn), 'w') as out:
                out.write(response)
        except Exception as e:
            print (ecli, e)
            failed_eclis.append(ecli)
        
    i += 1

