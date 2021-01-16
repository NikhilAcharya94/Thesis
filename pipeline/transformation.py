# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:16:32 2020

@author: Nikhil
"""

from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD,OWL,RDFS
import pandas as pd
import random
import re
import rdflib
from forex_python.converter import CurrencyRates


g = rdflib.Graph()
ITUNES_LEFT = Namespace("http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#")
ITUNES_RIGHT = Namespace("http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#")                       
itunes_left_str = "http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology"         
itunes_right_str = "http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology"
neighbor_dict={}
right_dict={}
left_dict={}
path_literal={}


def bfs_shortest_path(graph, start, goal):
    # keep track of explored nodes
    explored = []
    # keep track of all the paths to be checked
    queue = [[start]]
 
    # return path if start is goal
    if start == goal:
        return "That was easy! Start = goal"
 
    # keeps looping until all possible paths have been checked
    while queue:
        # pop the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        if node not in explored:
            neighbours = graph[node]
            # go through all neighbour nodes, construct a new path and
            # push it into the queue
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                # return path if neighbour is goal
                if neighbour == goal:
                    return new_path
 
            # mark node as explored
            explored.append(node)
 
    # in case there's no path between the 2 nodes
    return "So sorry, but a connecting path doesn't exist :("

def remove_prefix(text, prefix):
    if prefix==itunes_right_str:
        return "right_"+text[len(prefix)+1:]
    else:
        return "left_"+text[len(prefix)+1:]

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def path_to_literal(path_list):
    if(len(path_list)==2):
        path_list=path_list[1:]
        return(path_list)
    else:
        new_path_list=[]
        for index in range(0,len(path_list)-1):
            if(index==len(path_list)-2):
                new_path_list.append(path_list[len(path_list)-1])
            for class_obj in g.triples((None,None,OWL.ObjectProperty)):
                obj_domain=str([str(row[2]) for row in g.triples((class_obj[0],RDFS.domain,None))]).strip("['']")
                obj_range=str([str(row[2]) for row in g.triples((class_obj[0],RDFS.range,None))]).strip("['']")
                if(remove_prefix(obj_domain,obj_domain.split("#")[0])==path_list[index] and remove_prefix(obj_range,obj_range.split("#")[0])==path_list[index+1]):
                    new_path_list.append(remove_prefix(str(class_obj[0]),str(class_obj[0]).split("#")[0]))
                    break
        return(new_path_list)
    

    
    
def main():      
    g.parse ('output_file_merge.ttl', format='ttl')
    for class_song in g.triples((None,None,OWL.Class)):
        neighbor_list=[str(row[0]) for row in g.triples((None,RDFS.domain, class_song[0]))]
        neightbor_l_modified=[]
        for neighbor in neighbor_list:
            neighbor_check=str([str(check_d[0]) for check_d in g.triples((URIRef(neighbor),None, OWL.DatatypeProperty))]).strip("['']")
            if(neighbor_check==neighbor):
                neightbor_l_modified.append(remove_prefix(neighbor,neighbor.split("#")[0]))
            else:
                neighbor_object=str([str(check_o[2]) for check_o in g.triples((URIRef(neighbor),RDFS.range, None))]).strip("['']")
                neightbor_l_modified.append(remove_prefix(neighbor_object,neighbor_object.split("#")[0]))
            neighbor_dict[remove_prefix(str(class_song[0]),str(class_song[0]).split("#")[0])]=neightbor_l_modified


    for class_literal in g.triples((None,None,OWL.DatatypeProperty)):
        neightbor_l_modified=[]
        lit_domain=str([str(row[2]) for row in g.triples((class_literal[0],RDFS.domain,None))]).strip("['']")
        neightbor_l_modified.append(remove_prefix(lit_domain,lit_domain.split("#")[0]))
        neighbor_dict[remove_prefix(str(class_literal[0]),str(class_literal[0]).split("#")[0])]=neightbor_l_modified
    
    for key in neighbor_dict:
        if 'right' in key:
            right_dict[key] = neighbor_dict[key]
        else:
            left_dict[key] = neighbor_dict[key]


    itunes_col_list=['id','label']
    itunes_col_list=itunes_col_list+ list(neighbor_dict.keys())


    for class_obj in g.triples((None,None,OWL.ObjectProperty)):
        obj_domain=str([str(row[2]) for row in g.triples((class_obj[0],RDFS.domain,None))]).strip("['']")
        itunes_col_list = remove_values_from_list(itunes_col_list,remove_prefix(obj_domain,obj_domain.split("#")[0]))
        obj_prop=str([str(row[2]) for row in g.triples((class_obj[0],RDFS.range,None))]).strip("['']")
        itunes_col_list = remove_values_from_list(itunes_col_list,remove_prefix(obj_prop,obj_prop.split("#")[0]))                                                                                                                                                                                         
    
                                                 
    itunes_df = pd.DataFrame(columns = itunes_col_list)   
    

    columns=[column for column in itunes_df.columns  if column not in ["id","label"]]
    

    for column in columns:
        if 'right_' in column:
            path_literal[column]=path_to_literal(bfs_shortest_path(right_dict, 'right_Song', column))
        else:
            path_literal[column]=path_to_literal(bfs_shortest_path(left_dict, 'left_Song', column))

    row_num=0
    for left_song_id in g.triples((None,RDF.type,URIRef(itunes_left_str+"#"+"Song"))):
        song_id=int(str(left_song_id[0]).split("#")[1][:-1])
        itunes_df.loc[row_num, 'id']=song_id
        right_song_id=str([str(row[0]) for row in g.triples((URIRef(itunes_right_str+'#'+str(song_id)+'R'),RDF.type,URIRef(itunes_right_str+"#"+"Song")))]).strip("['']")
        label_v=str([str(label[1]) for label in g.triples((left_song_id[0],None,URIRef(right_song_id)))]).strip("['']")
        if(URIRef(label_v)==OWL.sameAs):
            itunes_df.loc[row_num, 'label']=1
        else:
            itunes_df.loc[row_num, 'label']=0
    
        columns=[column for column in itunes_df.columns  if column not in ["id","label"]]
    
        for column in columns:
            if 'right_' in column:
                value=[]
                for path in path_literal[column]:
                    relation=path.split("_")[1]
                    path_id=URIRef(itunes_right_str+"#"+relation)
                    if(not value):
                        value=str([str(row[2]) for row in g.triples((URIRef(right_song_id),path_id,None))]).strip("['']")
                    else:
                        value=str([str(row[2]) for row in g.triples((URIRef(value),path_id,None))]).strip("['']")
                
            else:
                value=[]
                for path in path_literal[column]:
                    relation=path.split("_")[1]
                    path_id=URIRef(itunes_left_str+"#"+relation)
                    if(not value):
                        value=str([str(row[2]) for row in g.triples((left_song_id[0],path_id,None))]).strip("['']")
                    else:
                        value=str([str(row[2]) for row in g.triples((URIRef(value),path_id,None))]).strip("['']") 
            itunes_df.loc[row_num,column]=value
        row_num=row_num+1
    
    itunes_df = itunes_df.reindex(sorted(itunes_df.columns), axis=1)
    itunes_df.drop(['right_Duration', 'left_Duration'], axis=1, inplace=True)
    

