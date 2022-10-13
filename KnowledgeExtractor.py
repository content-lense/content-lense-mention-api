import EntityCollector
import gender_guesser.detector as gender
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
genderDetector = gender.Detector()

class KnowledgeExtractor:
    def __init__(self,ec: EntityCollector):
        self.ec = ec

    def guessGenderFromName(self,name):
        nameParts=name.split()
        genders = [genderDetector.get_gender(part) for part in nameParts if genderDetector.get_gender(part) != "unknown"]
        gender = genders[0] if len(genders)>0 else None # for now just use the first non-unknown gender
        return  gender 

    def processNames(self,names,additionalInfo: Optional[dict] = None):
        genders = {}
        for name in names:
            gen = self.guessGenderFromName(name)
            if gen is not None:
                genders[name]={}
                genders[name]["genderFromName"] = gen
        
        if additionalInfo is None:
            myAdditionalInfo = genders
        else:
            myAdditionalInfo = {}
            myAdditionalInfo.update(additionalInfo)
            myAdditionalInfo.update(genders)
        
        notFound = self.ec.addEntitiesByName(names,additionalInfo=myAdditionalInfo)

        summary=[]
        for name in names:
            ent = self.ec.getMostLikelyEntityByName(name)

            if ent is not None and "genderFromWikiData" in ent:
                gen=ent["genderFromWikiData"]
            elif name in genders:
                gen = genders[name]["genderFromName"]
            else:
                gen = None

            if ent is not None and "dateOfBirth" in ent:
                birthday = datetime.strptime(ent["dateOfBirth"],'%Y-%m-%dT%H:%M:%SZ')
                age = relativedelta(datetime.now(),birthday).years
            else:
                age = None

            if ent is not None and "ethnicGroups" in ent:
                ethnicGroups = ent["ethnicGroups"]
            else:
                ethnicGroups = None
            
            if ent is not None and "sexualOrientation" in ent:
                sexualOrientation = ent["sexualOrientation"]
            else:
                sexualOrientation = None

            tmp={
                "name": name,
                "isKnown": name not in notFound,
                "gender": gen,
                "age": age,
                "ethnicGroups": ethnicGroups,
                "sexualOrientation": sexualOrientation
            }
            summary.append(tmp)

        report={"summary":summary}
        report["notFound"]=notFound

        return report


