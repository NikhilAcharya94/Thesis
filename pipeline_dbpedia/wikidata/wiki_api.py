#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 22:18:28 2021

@author: nacharya
"""

from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD,OWL,RDFS
import pandas as pd
import random
import re
import rdflib
from forex_python.converter import CurrencyRates
from SPARQLWrapper import SPARQLWrapper, N3,JSON
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
import urllib




sparql = SPARQLWrapper('http://dbpedia.org/sparql')
g = Graph()

sparql.setQuery("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {?wiki_class  rdf:type owl:Class}
WHERE
{
    ?item rdf:type owl:Class .
    ?item owl:equivalentClass ?wiki_class .
    #FILTER(STRSTARTS(STR(?wiki_class), 'https://www.wikidata.org'))
}
""")
sparql.setReturnFormat(N3)
results = sparql.query().convert()

g.parse(data=results,format="turtle")
wiki_ns=Namespace("http://www.wikidata.org/entity/")
prefix="http://www.wikidata.org/entity/"


for wiki_class in g.triples((None,None, None)):
    if(str(wiki_class[0])[:len(prefix)]!=prefix):
        g.remove((wiki_class))
    
    

    
g.serialize(destination="test_wiki_entities.ttl",format='turtle')