#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 20:55:30 2021

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
CONSTRUCT {?item owl:equivalentProperty ?wiki_class }
WHERE
{
    ?item rdf:type owl:ObjectProperty .
    ?item owl:equivalentProperty ?wiki_class .
    FILTER(STRSTARTS(STR(?wiki_class), 'http://www.wikidata.org/entity/'))
}
""")
sparql.setReturnFormat(N3)
results = sparql.query().convert()
g.parse(data=results,format="turtle")
g.serialize(destination="test_properties.ttl",format='turtle')