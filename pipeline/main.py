# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 20:58:31 2021

@author: Nikhil
"""

import individuals
import individuals_right
import sparql_test
import sparql_test_left
import graph_merge
import transformation
from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD
import pandas as pd
import random
import re

individuals.main("validaton_conflicts5.csv")
individuals_right.main("validation_conflicts5.csv")
sparql_test.main()
sparql_test_left.main()
graph_merge.main("validation_conflicts5.csv")
transformation.main()
