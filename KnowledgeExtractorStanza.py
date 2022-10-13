from KnowledgeExtractor import KnowledgeExtractor
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import reduce

class KnowledgeExtractorStanza(KnowledgeExtractor):
    def getUniquePersons(self,doc):
        perEnts = [ent for sent in doc.sentences for ent in sent.ents if ent.type=='PER']
        perEntsText = [ent.text for ent in perEnts]
        uniquePerEnts = [x for i, x in enumerate(perEnts) if i == perEntsText.index(x.text)]
        return uniquePerEnts

    def getSentencesForEntityName(self, doc, name):
        return [sent for sent in doc.sentences for ent in sent.ents if ent.text == name]

    def getUniqueSentenceTextsForEntityName(self, doc, name):
        sentences = self.getSentencesForEntityName(doc,name)
        return [sent.text for i,sent in enumerate(sentences) if i == sentences.index(sent)]
    # use like so:
    # sentences={person.text: getSentencesForEntityNameSpacy(doc,person.text) for person in uniquePersons}

    def getLookupListForEntities(self,entities):
        personsInGenitive = set([ent.text for ent in entities if ent.type=="PER" and  ent.words[0].feats is not None and "Case=Gen" in ent.words[0].feats])
        #personsNotGenitive = set([ent.text for sent in doc.sentences for ent in sent.ents if ent.type=="PER" and  ent.words[0].feats is not None and "Case=Gen" in ent.words[0].feats])
        personsSingularNotGenitive = [ent for ent in entities if ent.type=="PER" and  ent.words[0].feats is not None and "Case=Gen" not in ent.words[0].feats and "Number=Sing" in ent.words[0].feats]
        # genitive entities not ending with "s" are treated as normal lookup candidates
        genitiveCandidates = [name for name in personsInGenitive if name[-1] != "s"]
        # all others still have to be tested if they are already includend in the final lookup list we strip the s or if we keep it
        genitiveEntitiesEndingWithS = [name for name in personsInGenitive if name[-1] == "s"]
        
        # add non genitive entities to lookup candidates
        lookupCandidates = genitiveCandidates + [per.text for per in personsSingularNotGenitive]
        
        uniqueNames = list(set(lookupCandidates))

        uniqueGentivesEndingWithS = list(set(genitiveEntitiesEndingWithS))

        #uniqueNames = set([ent.text for ent in entities])
        splitNames = [name.split() for name in uniqueNames]
        nameFragments = [item[0] for item in splitNames if len(item) == 1] # assume we only have the first or lastname if the name only consists of single word
        fullNames = [item for item in splitNames if len(item) > 1] # assume we have the full name if the name consists of multiple parts. clearly this is not always true
        flattendedFullNameParts = [item for items in fullNames for item in items]
        
        # only keep genitive names as lookup candidtates if they are not already in the list entirely or with the s stripped
        additionalGenitiveCandidatesEndingWithS = [
                name for name in uniqueGentivesEndingWithS
                if (name not in uniqueNames and name[:-1] not in uniqueNames) # check full name equality
                and (name not in flattendedFullNameParts and name[:-1] not in flattendedFullNameParts) # check if genitive matches any partial name
            ]

        ### do the mapping of entitites where we can be almost sure they are identical
        # the inverse are gentives that have been mapped onto their non-genitive forms
        # full names can be mapped directly
        mappedFullNameGenitivesEndingWithS = {genitive: name for genitive in uniqueGentivesEndingWithS for name in uniqueNames if genitive[-1] == name} # if gentive == name, it is not a mapping, because the genitive is already included in the lookup list 

        # genitive name fragments that appear as part of a full name
        mappingCandidatesGenitiveFragmentsToFullName = [name for name in uniqueGentivesEndingWithS if (name in flattendedFullNameParts or name[:-1] in flattendedFullNameParts)]
        
        # single word entities that occur exactly once in a full name are mappable. in a closed world assumption we simple map the single word to the full name that includes the single word entity
        # NOTE that this mapping is only allowed within the analyzed document
        mappable = [frag for frag in nameFragments if flattendedFullNameParts.count(frag) == 1]
        mapped = {frag: " ".join(fullName) for frag in mappable for fullName in fullNames if frag in fullName}
        
        
        mappableGentiveFragments = [frag for frag in mappingCandidatesGenitiveFragmentsToFullName 
            if (
                (flattendedFullNameParts.count(frag) == 1 or flattendedFullNameParts.count(frag[:-1]) == 1) # the fragment should be included only once either with or with out trailing s
                and not 
                (flattendedFullNameParts.count(frag) == 1 and flattendedFullNameParts.count(frag[:-1]) == 1) # but not both

            )                
        
        ]
        mappedGenitiveFragments = {frag: " ".join(fullName) for frag in mappableGentiveFragments for fullName in fullNames if frag in fullName or frag[:-1] in fullName }

        mapped.update(mappedGenitiveFragments)        
        mapped.update(mappedFullNameGenitivesEndingWithS)

        ### collect ambiguous mappings of entities, where we can be almost sure they refer to some other entity in the text, but we don't know exactly which one

        # single word entities that accour more than one in a full name are ambiguous
        ambiguousFragments = [frag for frag in nameFragments if flattendedFullNameParts.count(frag) > 1]
        ambiguous = {frag: [" ".join(fullName) for fullName in fullNames if frag in fullName] for frag in ambiguousFragments}

        ambiguousGenitive = {frag: [" ".join(fullName) for fullName in fullNames if frag in fullName or frag[:-1] in fullName] for frag in mappingCandidatesGenitiveFragmentsToFullName if frag not in mappableGentiveFragments}
        ambiguous.update(ambiguousGenitive)

        # ignore single word entities that are not part of a full name
        ignoredFragments = [frag for frag in nameFragments if frag not in flattendedFullNameParts]

        # ignore single word gentitive entities that are not part of a full name, not even with the s stripped
        unmatchedGenitiveNameFragmentsEndingWithS = [name for name in additionalGenitiveCandidatesEndingWithS if len(name.split()) == 1]

        # full names (not split) that should be added to the lookup list
        unmatchedGenitiveFullNamesEndingWithS = [name for name in additionalGenitiveCandidatesEndingWithS if len(name.split()) > 1]


        # build a lookup list from unique full names
        lookupList = [" ".join(parts) for parts in fullNames]

        # add unmatched gentive full names to the lookup list
        lookupList += unmatchedGenitiveFullNamesEndingWithS

        
        return {"lookup":lookupList, "ignored":ignoredFragments+unmatchedGenitiveNameFragmentsEndingWithS, 'mapped':mapped, 'ambiguous':ambiguous}
    
    def guessGenderFromGrammaticalGender(self,entity):
        """
            Derive real word gender (male or female) from grammatical gender
            Empirical tests imply that stanza will assign gender "Masc" if in doubt.
            E.g. Christina Hebel -> Fem Masc but Carl Blume -> Masc Masc
        """
        femaleDetected = reduce(lambda agg, new: agg or ((new.feats is not None) and "Fem" in new.feats) ,entity.words,False)
        return "female" if femaleDetected else "male"


    def processDoc(self,doc, produceTrainingData=False):
        uniquePersons = self.getUniquePersons(doc)

        # generate a lookup list
        lookup = self.getLookupListForEntities(uniquePersons)

        #guess genders
        genders = {}

        for entity in uniquePersons:
            name=entity.text
            genders[name] = {}
            genders[name]["genderFromGrammar"] = self.guessGenderFromGrammaticalGender(entity)
            gen = self.guessGenderFromName(name)
            if gen is not None:
                genders[name]["genderFromName"] = gen

        notFound = self.ec.addEntitiesByName(lookup["lookup"],additionalInfo=genders)        
    
        if produceTrainingData:
            trainingSentences = {person.text: self.getUniqueSentenceTextsForEntityName(doc,person.text) for person in uniquePersons}
        
        # create statistics
        # count mentions
        entityTexts = [ent.text for sent in doc.sentences for ent in sent.ents]
        numberOfMentions = {person.text: entityTexts.count(person.text) for person in uniquePersons}
        
        # add mapped mentions
        for shortName, mappedTo in lookup['mapped'].items():
            numberOfMentions[mappedTo]+=numberOfMentions[shortName]
            del numberOfMentions[shortName]
        
        summary=[]
        for name in uniquePersons:
            if name.text in lookup['mapped']:
                continue

            ent = self.ec.getMostLikelyEntityByName(name.text)

            if ent is not None and "genderFromWikiData" in ent:
                gen=ent["genderFromWikiData"]
                genType='kb'
            elif name.text in genders and  "genderFromName" in genders[name.text]:
                gen = genders[name.text]["genderFromName"]
                genType = 'name'
            elif name.text in genders:
                gen = genders[name.text]["genderFromGrammar"]
                genType = 'gram'
            else:
                gen = None
                genType = None

            if ent is not None and "dateOfBirth" in ent:
                try:
                    birthday = datetime.strptime(ent["dateOfBirth"],'%Y-%m-%dT%H:%M:%SZ')
                    age = relativedelta(datetime.now(),birthday).years
                except Exception as e:
                    print(e)
                    age = None
            else:
                age = None

            tmp={
                "name": name.text,
                "isKnown": name.text not in notFound and name.text not in lookup["ignored"],
                "gender": gen,
                "genderSource": genType,
                "mentionCount": numberOfMentions[name.text],
                "age": age
            }
            summary.append(tmp)

        report={"summary":summary}
        report.update(lookup)
        report["notFound"]=notFound
        if produceTrainingData:
            report["trainingSentences"] = trainingSentences
        
        return report
        
