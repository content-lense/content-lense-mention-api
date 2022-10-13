
import wikiDataEntityLoader
from importlib import reload
reload(wikiDataEntityLoader)
from wikiDataEntityLoader import WikiDataEntityLoader
import re
from typing import Optional
from functools import reduce

class EntityCollector:
    lookupTypeWeights={"exact": 1.0, "fuzzy":0.9, "fulltext":0.8}
    altLabelMatchBonusFactors={"exact": 1.0, "fuzzy":10, "fulltext":100} #increase the score of the match if the original name is included in the altLabels

    def __init__(self):
        self.el=WikiDataEntityLoader()
        self.matchQId = re.compile("Q[0-9]*")
        self.synonyms={} #label: [{qid, weight}]
        self.entities = {} # qid: {all info for qid}
        self.notFoundInWikiData=[]
        
    
    def lookupWikiDataFromList(self,lookupList):
        wikiDataResults={}
        for name in lookupList:
            lookupType="exact"
            res=self.el.getEntityExact(name,10)
            if (len(res)==0):
                #print(f"  Performing fuzzy label search for {name}")
                lookupType="fuzzy"
                res = self.el.getEntityFuzzy(name,10)
            if (len(res)==0):
                lookupType="fulltext"
                #print(f"  Performing fulltext search for {name}")
                res = self.el.getEntityFulltext(name,10)
            #print(f"{len(res)} results found for {name}")
            wikiDataResults[name]={"lookupType": lookupType, "results": res}
        return wikiDataResults

    def lookupWikiData(self,name):
        lookupType="exact"
        res=self.el.getEntityExact(name,10)
        if (len(res)==0):
            lookupType="fuzzy"
            res = self.el.getEntityFuzzy(name,10)
        if (len(res)==0):
            lookupType="fulltext"
            res = self.el.getEntityFulltext(name,10)
        return {"lookupType": lookupType, "results": res}

    def getRelativeMatchWeights(self,results,searchTerm ="", matchType = 'exact'):
        absWeights=[max(1,int(item["statements"]["value"])+int(item["sitelinks"]["value"])) for item in results] # max(1,...) avoids a weight of zero in case no statements or sitelinks are present
        #apply altLabel bonus
        if (matchType != 'exact'):
            absWeights = [self.altLabelMatchBonusFactors[matchType] * w if searchTerm in results[list(results)[i]]["altLabels"]["value"] else w for i,w in enumerate(absWeights)]
        total = 1.0 * sum(absWeights)
        return [w/total for w in absWeights]

    def addWeightsToWikiMatches(self,matches):
        weights=self.getRelativeMatchWeights(matches['results'],matches['lookupType'])
        for i,match in enumerate(matches['results']):
            qid=re.search("Q[0-9]*",match["human"]["value"])[0]
            label=match['humanLabel']['value']
            description=match['humanDescription']['value']
            weight = weights[i]
            match.update({"qid":qid, "label": label, "description":description, "weight":weight})
            #print(f" {i+1} {match['humanLabel']['value']}\t{match['humanDescription']['value']}\t{qid}\t{weights[i]}\t{weights[i]*lookupTypeWeights[matches['lookupType']]}")
        return matches

    def unpackAndWeightWikiMatches(self,matches):
        weights=self.getRelativeMatchWeights(matches['results'],matches['lookupType'])
        unpacked=[]
        for i,match in enumerate(matches['results']):
            u={}
            u["qid"] = re.search("Q[0-9]*",match["human"]["value"])[0]
            u["label"] = match['humanLabel']['value']
            # should we really use and entity match if it does not have a description?
            if 'humanDescription' not in match:
                continue
            u["description"]=match['humanDescription']['value']
            u["sitelinks"] = int(match['sitelinks']['value'])
            u["statement"] = int(match['statements']['value'])
            u["weight"] = weights[i]
            u["wikiDataResult"] = match
            u["lookupType"] = matches["lookupType"]
            unpacked.append(u)
            #print(f" {i+1} {match['humanLabel']['value']}\t{match['humanDescription']['value']}\t{qid}\t{weights[i]}\t{weights[i]*lookupTypeWeights[matches['lookupType']]}")
        return unpacked

    def addEntitiesByName(self,nameList,fetchDetails=True,additionalInfo: Optional[dict] = None): #additional info is a dict with names as key. contents will be added to all found entities
        notFound=[]
        for name in nameList:
            if (name in self.synonyms): # for now simply skip the name if we already have it in the list of synonms
                continue
            if (name in self.notFoundInWikiData):
                notFound.append(name)
                continue
            try:
                wikiData=self.lookupWikiData(name)
                if (len(wikiData["results"])>0):
                    #self.addWeightsToWikiMatches(wikiData)
                    #self.synonyms[name]=[{"qid": match["qid"],"weight":match["weight"]} for match in wikiData["results"]]
                    #for match in wikiData["results"]:
                    #    self.entities[match["qid"]]=match
                    unpacked = self.unpackAndWeightWikiMatches(wikiData)
                    # unpacked will have a length of 0 if none of the matches included a description
                    # in this case we regard the name as not found in wiki data, because it will be of no use for us
                    if len(unpacked) == 0:
                        notFound.append(name)
                        continue
                    self.synonyms[name]=[{"qid": match["qid"],"weight":match["weight"],"lookupType":match["lookupType"]} for match in unpacked]
                    for match in unpacked:
                        if additionalInfo is not None and name in additionalInfo:
                            match.update(additionalInfo[name])
                        self.entities[match["qid"]]=match
                        if fetchDetails:
                            self.addWikiDataDetailsToEntity(match["qid"])
                else:
                    self.notFoundInWikiData.append(name)
                    notFound.append(name)
            except Exception as e:
                print(e)
                print(f"Error when looking up {name}. Skipping...")
                notFound.append(name)
        return notFound

    def getCandidatesByName(self,name):
        if name in self.synonyms:
            return self.synonyms[name]

    def getEntitiesByName(self,name):
        return [self.entities[synonym["qid"]] for synonym in self.synonyms[name]]

    def getMostLikelyEntityByName(self, name):
        candidates = self.getCandidatesByName(name)
        if candidates is not None:
            candidate = reduce(lambda agg, el: agg if agg["weight"] > el["weight"] else el, candidates)
            return self.entities[candidate["qid"]]

    def addDataToEntity(self,qid,data: dict):
        self.entities[qid].update(data)

    def addWikiDataDetailsToEntity(self, qid):
        wikiData=self.el.getDetails(qid)
        if (len(wikiData)>0):
            if ("genderLabel" in wikiData[0]):
                self.entities[qid]["genderFromWikiData"] = wikiData[0]["genderLabel"]["value"]
            if ("countryOfBirthLabel" in wikiData[0]):
                self.entities[qid]["countryOfBirth"] = wikiData[0]["countryOfBirthLabel"]["value"]
            if ("dateOfBirth" in wikiData[0]):
                self.entities[qid]["dateOfBirth"] = wikiData[0]["dateOfBirth"]["value"]
            if ("placeOfBirthLabel" in wikiData[0]):
                self.entities[qid]["placeOfBirth"] = wikiData[0]["placeOfBirthLabel"]["value"]
            if ("citizenshipLabels" in wikiData[0]):
                self.entities[qid]["citizenships"] = wikiData[0]["citizenshipLabels"]["value"].split("; ")
            if ("religionLabels" in wikiData[0]):
                self.entities[qid]["religions"] = wikiData[0]["religionLabels"]["value"].split("; ")
            if ("ethnicGroupLabels" in wikiData[0]):
                self.entities[qid]["ethnicGroups"] = wikiData[0]["ethnicGroupLabels"]["value"].split("; ")
            if ("image" in wikiData[0]):
                self.entities[qid]["image"] = wikiData[0]["image"]["value"]
            if ("sexualOrientationLabel" in wikiData[0]):
                self.entities[qid]["sexualOrientaion"] = wikiData[0]["sexualOrientationLabel"]["value"].split("; ")
            
            self.entities[qid]["wikiDataResult"].update(wikiData[0])
