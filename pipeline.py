import os
from dotenv import load_dotenv
import pandas as pd
import stanza
from EntityCollector import EntityCollector
from KnowledgeExtractorStanza import KnowledgeExtractorStanza
import pickle


## for image download
from pathlib import Path
from PIL import Image
import requests

load_dotenv()


nlp = stanza.Pipeline('de',processors="tokenize,mwt,pos,ner") # if preprocessesors is not set, all preprocessors are used

# import Entity Collector. This holds all information on the entities and should be global


# read entity collector from file, if it exists
if os.path.isfile('entityCollector.pkl'):
    with open('entityCollector.pkl','rb') as input:    
        ec = pickle.load(input)
else:
    ec=EntityCollector()
#  import Knowledge Extractor. This provides a simple interface to gather information about the recognized entities

ke = KnowledgeExtractorStanza(ec)



def processAuthors(authors):

    # add authors to entity collection
    # guess genders from name
    additionalInfo = {}
    for author in authors:
        name = author['name']
        additionalInfo[name]={}
        additionalInfo[name]['isSameAs']={}
        additionalInfo[name]['isSameAs']['externalId'] = author["externalId"]

    res = ke.processNames([author['name'] for author in authors], additionalInfo)


    # for each author simply guess the gender by name and update the database
    for author in authors:
        gen = ke.guessGenderFromName(author['name'])
        if gen is not None:
            author['genderFromName'] = gen

    df = pd.DataFrame(res["summary"])
    df.groupby('gender').count()


def processIfNotEmpty(text,createTrainingSentences=False):
    if text is not None and (len(text.strip())>0):
        doc = nlp(text.replace('\xa0',' ').replace('\n',' ')) # remove unbreakable white space as a quick fix where it's accurance breaks the mapping from single word entities to full names. probably because we re-join the entities with spaces for the mapping but not for the original full name. this causes a key error in line 146 of KnowledgeExtractorStanza . remove all new lines from text. not sure if this is a good ides
        res = ke.processDoc(doc,createTrainingSentences)
    else:
        res = None

    return res

def summarize(res):
    if res['heading'] is not None:
        hdf = pd.DataFrame(res['heading']['summary'])
    else:
        hdf = pd.DataFrame()
    if res['summary'] is not None:
        sdf = pd.DataFrame(res['summary']['summary'])
    else:
        sdf = pd.DataFrame()
    if res['body'] is not None:
        bdf = pd.DataFrame(res['body']['summary'])
    else:
        bdf = pd.DataFrame()
    df = pd.concat([hdf,sdf,bdf])
    stats=None
    if 'gender' in df.columns: 
        stats={}
        genderGroups=df.groupby('gender')
        for name, group in genderGroups:
            stats[name]={'count': int(group['name'].count())}
    return stats

def processArticle(article):
    print(f"Processing article ({article['id']}): {article['heading']}")
    print("   Analysing headline")
    headlineRes = processIfNotEmpty(article['heading'],True)
    print("   Analysing Summary")
    summaryRes = processIfNotEmpty(article['summary'],True)
    print("   Analysing body")
    bodyRes = processIfNotEmpty(article['body'],True)
  

    res = {
        'id': article['id'],
        'heading': headlineRes,
        'summary':summaryRes,
        'body':bodyRes
    }

    print("   Summarizing")
    stats = summarize(res)

    try:
        persistKnowlege()
    except:
        pass
    
    return {'result': res, 'stats': stats }


def persistKnowlege():
    print("Saving entity collector")
    with open('entityCollector.pkl','wb') as output:    
        pickle.dump(ec,output,pickle.HIGHEST_PROTOCOL)   


# download entity images
def downloadEntityImages():
    compressImages=True
    for qid, entity in ec.entities.items():
        if 'image' in entity:
            path = os.path.join(os.getenv('IMAGE_PATH'),qid)
            filename = entity['image'].split('/')[-1]
            fullpath = os.path.join(path,filename)
            #download missing files
            if not os.path.isfile(fullpath):
                Path(path).mkdir(parents=True, exist_ok=True)
                img = requests.get(entity['image'],allow_redirects=True)
                with open(fullpath,'wb') as file:
                    file.write(img.content)
                if compressImages:
                    pimg = Image.open(fullpath)
                    pimg.thumbnail((1024,1024)) # thumbnail keeps the aspect ratio and only resizes if the image will become smaller
                    pimg.save(fullpath,optimize=True) #overwrite original image
                
