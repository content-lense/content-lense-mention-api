# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
#!{sys.executable} -m pip install sparqlwrapper
from SPARQLWrapper import SPARQLWrapper, JSON

class WikiDataEntityLoader:
    def __init__(self):
      self.endpoint_url = "https://query.wikidata.org/sparql"

      self.user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
      # TODO adjust user agent; see https://w.wiki/CX6
      self.sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)

    detailsFulltextQuery = """# Person nach volltext suchen
SELECT
?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?ethnicGroupLabel ?sexualOrientationLabel ?citizenshipLabel 
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates 
?image ?religion
WHERE
{
 SERVICE wikibase:mwapi {
   bd:serviceParam wikibase:endpoint "www.wikidata.org";
   wikibase:api "Search";
   wikibase:apiOrdinal true ;
   mwapi:srsearch "{1}";  # Search for things named "front matter"
   mwapi:language "de".
   ?human wikibase:apiOutputItem mwapi:title.
 }
  ?human wdt:P31 wd:Q5 .       #find humans
 # ?human skos:altLabel ?altLabel . FILTER (contains(?altLabel, "{1}"@de)).
  optional {?human wdt:P21 ?gender .}
  optional {?human wdt:P172 ?ethnicGroup .}
  optional {?human wdt:P27 ?citizenship .}
  optional {?human wdt:P19 ?placeOfBirth .
  ?human wdt:P19/wdt:P625 ?placeOfBirthCoordinates .
  ?human wdt:P19/wdt:P17 ?countryOfBirth .}
  optional {?human wdt:P569 ?dateOfBirth .}
  # ?human wdt:P106 ?occupation .
  optional { ?human wdt:P18 ?image .}
  # ?human wdt:P140 ?religion .
  optional {  ?human wdt:P91 ?sexualOrientation .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
limit {2}"""


    detailsFuzzyLabelQuery = """# Person nach label suchen
SELECT
?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?ethnicGroupLabel ?sexualOrientationLabel ?citizenshipLabel 
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates 
?image ?religion
WHERE
{
 SERVICE wikibase:mwapi {
   bd:serviceParam wikibase:endpoint "www.wikidata.org";
   wikibase:api "EntitySearch";
   wikibase:apiOrdinal true ;
   mwapi:search "{1}";  # Search for things named "front matter"
   mwapi:language "de".
   ?human wikibase:apiOutputItem mwapi:item.
 }
  ?human wdt:P31 wd:Q5 .       #find humans
  #?human skos:altLabel ?altLabel . FILTER (contains(?altLabel, "{1}"@de)).
  optional {?human wdt:P21 ?gender .}
  optional {?human wdt:P172 ?ethnicGroup .}
  optional {?human wdt:P27 ?citizenship .}
  optional {?human wdt:P19 ?placeOfBirth .
  ?human wdt:P19/wdt:P625 ?placeOfBirthCoordinates .
  ?human wdt:P19/wdt:P17 ?countryOfBirth .}
  optional {?human wdt:P569 ?dateOfBirth .}
  # ?human wdt:P106 ?occupation .
  optional { ?human wdt:P18 ?image .}
  # ?human wdt:P140 ?religion .
  optional {  ?human wdt:P91 ?sexualOrientation .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
limit {2}"""

    detailsExactLabelQuery = """# Personendetails nach label suchen
SELECT
?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?ethnicGroupLabel ?sexualOrientationLabel ?citizenshipLabel 
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates 
?image ?religion
WHERE
{
  ?human wdt:P31 wd:Q5 .       #find humans
  ?human rdfs:label "{1}"@de .   # require that rdfs:label of the ?human entity contains the text "Anne Will" in the german field
  optional {?human wdt:P21 ?gender .}
  optional {?human wdt:P172 ?ethnicGroup .}
  optional {?human wdt:P27 ?citizenship .}
  optional {?human wdt:P19 ?placeOfBirth .
  ?human wdt:P19/wdt:P625 ?placeOfBirthCoordinates .
  ?human wdt:P19/wdt:P17 ?countryOfBirth .}
  optional {?human wdt:P569 ?dateOfBirth .}
  # ?human wdt:P106 ?occupation .
  optional { ?human wdt:P18 ?image .}
  # ?human wdt:P140 ?religion .
  optional {  ?human wdt:P91 ?sexualOrientation .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
limit {2}"""

    detailsFromIdQuery_bkp = """# Personendetails nach QID suchen
SELECT
?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?ethnicGroupLabel ?sexualOrientationLabel ?citizenshipLabel 
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates 
?image ?religion
WHERE
{
  BIND (wd:{QID} as ?human) .
  optional {?human wdt:P21 ?gender .}
  optional {?human wdt:P172 ?ethnicGroup .}
  optional {?human wdt:P27 ?citizenship .}
  optional {?human wdt:P19 ?placeOfBirth .
  ?human wdt:P19/wdt:P625 ?placeOfBirthCoordinates .
  ?human wdt:P19/wdt:P17 ?countryOfBirth .}
  optional {?human wdt:P569 ?dateOfBirth .}
  # ?human wdt:P106 ?occupation .
  optional { ?human wdt:P18 ?image .}
  # ?human wdt:P140 ?religion .
  optional {  ?human wdt:P91 ?sexualOrientation .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
limit {2}"""

    detailsFromIdQuery = """# Personensdetails nach QID mit gruppierten labels
  SELECT
?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?sexualOrientationLabel
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates ?image (group_concat(DISTINCT ?citizenshipLabel; SEPARATOR="; ") AS ?citizenshipLabels)
 (group_concat(DISTINCT ?religionLabel; SEPARATOR="; ") AS ?religionLabels) (group_concat(DISTINCT ?ethnicGroupLabel; SEPARATOR="; ") AS ?ethnicGroupLabels)
WHERE
{
  BIND (wd:{QID} as ?human) .
  ?human rdfs:label ?hl . # this line is a dummy line to ensure the entity does have a label, which we take as a minimum requirement for the existance of the entity
  optional {?human wdt:P21 ?gender .
    ?gender rdfs:label ?genderLabel . Filter(lang(?genderLabel)='en')
  }
  optional {?human wdt:P172 ?ethnicGroup .
           ?ethnicGroup rdfs:label ?ethnicGroupLabel . filter(lang(?ethnicGroupLabel)='de')
  }
  optional {?human wdt:P27 ?citizenship .
           ?citizenship rdfs:label ?citizenshipLabel . filter(lang(?citizenshipLabel)='de')
  }
  optional {?human wdt:P19 ?placeOfBirth .
  ?human wdt:P19/wdt:P625 ?placeOfBirthCoordinates .
  ?human wdt:P19/wdt:P17 ?countryOfBirth .}
  optional {?human wdt:P569 ?dateOfBirth .}
  # ?human wdt:P106 ?occupation .
  optional { ?human wdt:P18 ?image .}
  optional { ?human wdt:P140 ?religion .
            ?religion rdfs:label ?religionLabel . filter(lang(?religionLabel)='de')
  }
  optional {  ?human wdt:P91 ?sexualOrientation .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de" }
}
group by ?human ?humanLabel ?humanDescription ?dateOfBirth ?genderLabel ?sexualOrientationLabel
?countryOfBirthLabel ?placeOfBirthLabel ?placeOfBirthCoordinates ?image
limit 1 # always limit to one in order to circumvent row multiplication
  """


    fulltextQuery = """# Person nach volltext suchen
SELECT distinct
?human ?humanLabel ?humanDescription ?statements ?sitelinks (group_concat(DISTINCT ?altLabel; SEPARATOR="; ") AS ?altLabels)
WHERE
{
 SERVICE wikibase:mwapi {
   bd:serviceParam wikibase:endpoint "www.wikidata.org";
   wikibase:api "Search";
   wikibase:apiOrdinal true ;
   mwapi:srsearch "{1}";  # Search for things named "front matter"
   mwapi:language "de".
   ?human wikibase:apiOutputItem mwapi:title.
 }
  ?human wdt:P31 wd:Q5 .       #find humans
  optional {
    ?human skos:altLabel ?altLabel . filter(lang(?altLabel)='de')
  }
  ?human wikibase:statements ?statements .
  ?human wikibase:sitelinks ?sitelinks .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
group by ?human ?humanLabel ?humanDescription ?statements ?sitelinks
limit {2}"""


    fuzzyLabelQuery = """# Person nach label suchen
SELECT distinct
?human ?humanLabel ?humanDescription ?statements ?sitelinks (group_concat(DISTINCT ?altLabel; SEPARATOR="; ") AS ?altLabels)
WHERE
{
 SERVICE wikibase:mwapi {
   bd:serviceParam wikibase:endpoint "www.wikidata.org";
   wikibase:api "EntitySearch";
   wikibase:apiOrdinal true ;
   mwapi:search "{1}";  # Search for things named "front matter"
   mwapi:language "de".
   ?human wikibase:apiOutputItem mwapi:item.
 }
  ?human wdt:P31 wd:Q5 .       #find humans
  optional {
    ?human skos:altLabel ?altLabel . filter(lang(?altLabel)='de')
  }
  ?human wikibase:statements ?statements .
  ?human wikibase:sitelinks ?sitelinks .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
group by ?human ?humanLabel ?humanDescription ?statements ?sitelinks
limit {2}"""


    exactLabelQuery = """# Person nach label suchen
SELECT distinct
?human ?humanLabel ?humanDescription ?statements ?sitelinks
WHERE
{
  ?human wdt:P31 wd:Q5 .       #find humans
  ?human rdfs:label "{1}"@de .   # require that rdfs:label of the ?human entity contains the text "Anne Will" in the german field
  ?human wikibase:statements ?statements .
  ?human wikibase:sitelinks ?sitelinks .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en" }
}
limit {2}"""

    def get_results(self, query,timeout=30):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(timeout)
        return self.sparql.query().convert()

    def getEntityExact(self,text: str , limit: int = 5): 
        results = self.get_results(self.exactLabelQuery.replace("{1}",text).replace("{2}","5"))
        return results["results"]["bindings"]
    
    def getEntityFuzzy(self,text: str , limit: int = 5): 
        results = self.get_results(self.fuzzyLabelQuery.replace("{1}",text).replace("{2}","5"))
        return results["results"]["bindings"]
    
    def getEntityFulltext(self,text: str , limit: int = 5): 
        results = self.get_results(self.fulltextQuery.replace("{1}",text).replace("{2}","5"))
        return results["results"]["bindings"]
    
    def getDetails(self,qid: str):
        results = self.get_results(self.detailsFromIdQuery.replace("{QID}",qid).replace("{2}","5"))
        return results["results"]["bindings"]
    