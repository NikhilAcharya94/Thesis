# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 20:36:33 2020

@author: Nikhil
"""


from rdflib import Graph, Literal, RDF, URIRef,Namespace,OWL
from rdflib.namespace import XSD
import pandas as pd
import random
import re
import rdflib

g_merge = rdflib.Graph()
ITUNES_RIGHT = "http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#"
ITUNES_LEFT = "http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#"   



def main(file):
    g_merge.parse('output_file_right_conflicts.ttl',format='ttl')    
    g_merge.parse('output_file_conflicts.ttl',format='ttl')    
    label_df=pd.read_csv(file)
    columns_list=['id','label']
    label_df=label_df[columns_list]

    for index, row in label_df.iterrows():
        if(row["label"]==1):
            left_id=ITUNES_LEFT+str(int(row["id"]))+"L"
            right_id=ITUNES_RIGHT+str(int(row["id"]))+"R"
            g_merge.add((URIRef(left_id),OWL.sameAs,URIRef(right_id)))
        else:
            left_id=ITUNES_LEFT+str(int(row["id"]))+"L"
            right_id=ITUNES_RIGHT+str(int(row["id"]))+"R"
            g_merge.add((URIRef(left_id),OWL.differentFrom,URIRef(right_id)))

    g_merge.serialize('output_file_merge.ttl',format='ttl') 