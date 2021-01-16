#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 16:51:20 2021

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


def remove_prefix(text, prefix):
    return text[len(prefix):]

g=Graph()
g.parse ('test_entities.ttl', format='turtle')
for class_obj in g.triples((None,None, OWL.Class)):
    count_mapping=0
    for data_obj in g.triples((None,None, OWL.DatatypeProperty)):
        for data_class_obj in g.triples((data_obj[0],RDFS.domain,class_obj[0])):
            count_mapping=count_mapping+1
    for obj_prop in g.triples((None,None, OWL.ObjectProperty)):
        for obj_domain_obj in g.triples((obj_prop[0],RDFS.domain,class_obj[0])):
            count_mapping=count_mapping+1
        for obj_domain_obj in g.triples((obj_prop[0],RDFS.range,class_obj[0])):
            count_mapping=count_mapping+1
    if(count_mapping==0):
        g.remove((class_obj[0],class_obj[1],OWL.Class))
        g.remove((None,None,class_obj[0]))
        
        
for obj_prop in g.triples((None,None, OWL.ObjectProperty)):
    obj_domain=str([str(row[2]) for row in g.triples((obj_prop[0],RDFS.domain,None))]).strip("['']") 
    obj_range =str([str(row[2]) for row in g.triples((obj_prop[0],RDFS.range,None))]).strip("['']") 
    domain_check=str([str(row[0]) for row in g.triples((URIRef(obj_domain),None, OWL.Class))]).strip("['']")
    range_check=str([str(row[0]) for row in g.triples((URIRef(obj_range),None, OWL.Class))]).strip("['']")
    sub_prop_check=str([str(row[0]) for row in g.triples((None,RDFS.subPropertyOf, obj_prop[0]))]).strip("['']")
    if((obj_domain=='' or obj_range =='') and sub_prop_check=='' ):
        g.remove((obj_prop[0],None,OWL.ObjectProperty))
        g.remove((obj_prop[0],RDFS.range,None))
        g.remove((obj_prop[0],RDFS.domain,None))
        g.remove((obj_prop[0],RDFS.subPropertyOf, None))
    '''
    if(range_check==''):
        g.remove((obj_prop[0],None,OWL.ObjectProperty))
        g.remove((obj_prop[0],RDFS.range,None))
        g.remove((obj_prop[0],RDFS.domain,None))
        g.remove((obj_prop[0],RDFS.subPropertyOf, None))
    '''


for data_prop in g.triples((None,None, OWL.DatatypeProperty)):
    dat_domain=str([str(row[2]) for row in g.triples((data_prop[0],RDFS.domain,None))]).strip("['']") 
    dat_range =str([str(row[2]) for row in g.triples((data_prop[0],RDFS.range,None))]).strip("['']") 
    sub_prop_check=str([str(row[0]) for row in g.triples((None,RDFS.subPropertyOf, data_prop[0]))]).strip("['']")
    if((dat_domain=='' or dat_range =='') and sub_prop_check=='' ):
        g.remove((data_prop[0],None,OWL.DatatypeProperty))
        g.remove((data_prop[0],RDFS.range,None))
        g.remove((data_prop[0],RDFS.domain,None))
        g.remove((data_prop[0],RDFS.subPropertyOf, None))
    
    
    


g.serialize(destination="test_filter_entities.ttl",format='turtle')
