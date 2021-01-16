#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:08:31 2021

@author: nacharya
"""

from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD,OWL,RDFS
import pandas as pd
import random
import re
import rdflib
from forex_python.converter import CurrencyRates
from SPARQLWrapper import SPARQLWrapper, N3
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
import urllib
s = "abc \n \t \t\t \t \nefg"


def validate_uri(uri_str):
    uri_str=uri_str.replace(" ","")
    uri_str=re.sub('[^A-Za-z0-9]+', '', uri_str)
    return uri_str




def write_to_ttl(rel):
    
    try:
        sparql.setQuery("PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> CONSTRUCT { <"+rel+"> rdf:type ?type .  <"+rel+"> rdfs:domain ?domain . <"+rel+"> rdfs:range ?range . <"+rel+"> rdfs:subPropertyOf ?sub . }  WHERE { <"+rel+"> rdf:type ?type . OPTIONAL {<"+rel+"> rdfs:domain ?domain } OPTIONAL  {<"+rel+"> rdfs:range ?range } OPTIONAL  {<"+rel+"> rdfs:subPropertyOf ?sub } FILTER(STRSTARTS(STR(?type), 'http://www.w3.org/2002/07/owl#'))}")
        sparql.setReturnFormat(N3)
        results = sparql.query().convert()
        results=str(results,"utf-8")
        g_temp = Graph()
        g.parse(data=results,format="turtle")
    except urllib.error.URLError:
        print("Some other error happened")



with open("predicate_local_name_1.txt", "r") as f:
    rel = f.readlines()
rel = [x.split("\t")[0] for x in rel] 


sparql = SPARQLWrapper("http://dbpedia.org/sparql")
g = Graph()
g.parse ('test_entities.ttl', format='turtle')
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
#num_cores = multiprocessing.cpu_count()
#inputs = tqdm(entity)
prefix='http://dbpedia.org/ontology/'

for r in rel:
    if((':' in r[len(prefix):]) or (';' in r[len(prefix):]) or (',' in r[len(prefix):]) or ('-' in r[len(prefix):]) or (')' in r[len(prefix):]) or ('&' in r[len(prefix):]) or ("'" in r[len(prefix):]) or ("." in r[len(prefix):]) or ("!" in r[len(prefix):]) or ("%" in r[len(prefix):]) ):
        continue
    else:
        write_to_ttl(r)
        print(r)
    
     
g.serialize(destination="test_entities.ttl",format='turtle')







