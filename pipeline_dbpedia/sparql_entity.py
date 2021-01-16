#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 03:34:44 2021

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

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
   
SELECT  ?type  WHERE 
{ 
  <http://dbpedia.org/resource/Women_&_Men_2> rdf:type ?type .
}
""")

sparql.setReturnFormat(N3)
results = sparql.query().convert()
g = Graph()
g.parse(data=results, format="turtle")
print(g.serialize("test2.ttl",format='turtle'))