# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 19:49:13 2020

@author: Nikhil
"""

from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD
import pandas as pd
import random
import re
import rdflib

ITUNES = Namespace("http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#")
ENTITY = Namespace("http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#")
g = rdflib.Graph()                 

def validate_uri(uri_str):
    uri_str=uri_str.replace(" ","")
    uri_str=re.sub('[^A-Za-z0-9]+', '', uri_str)
    return uri_str

def split_price(price_string):
    if(price_string =="Album Only"):
        return "Album Only",0
    price_split_list=re.split('(\d+)',price_string)
    currency=price_split_list[0]
    currency=currency.replace(" ","")
    price=''.join(price_split_list[1:])
    price=float(price)
    return currency,price

def relations_genre(genre_string,uri_genre,uri_relation):
    genre_name=Literal(genre_string,datatype=XSD.string)
    g.add((URIRef(uri_genre),uri_relation ,genre_name))


def populate_rdf(Entity_df):
    Itunes_ns_string="http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#"
    Entity_ns_string="http://www.semanticweb.org/nikhil/ontologies/right/Itunes-Ontology#"
    for index, row in Entity_df.iterrows():
        entity_id=Entity_ns_string+str(int(row["id"]))+"R"
        album_entity=Entity_ns_string+ validate_uri(row["Album_Name"])
        artist_entity=Entity_ns_string+validate_uri(row["Artist_Name"])
        Time_entity=Entity_ns_string+str(int(row["id"]))+"R"+"Time"
        Price_entity=Entity_ns_string+str(int(row["id"]))+"R"+"Price"
        Genre_entity=Entity_ns_string+str(int(row["id"]))+"R"+"Genre"
        #Class Definition
        g.add((URIRef(entity_id), RDF.type, ITUNES.Song))
        g.add((URIRef(album_entity), RDF.type, ITUNES.Album))
        g.add((URIRef(artist_entity), RDF.type, ITUNES.Artist))
        g.add((URIRef(Time_entity), RDF.type, ITUNES.Time))
        g.add((URIRef(Price_entity), RDF.type, ITUNES.Price))
        g.add((URIRef(Genre_entity), RDF.type, ITUNES.Genre))
        #Object properties
        g.add((URIRef(entity_id),ITUNES.IsFrom ,URIRef(album_entity)))
        g.add((URIRef(album_entity),ITUNES.HasSong ,URIRef(entity_id)))
        g.add((URIRef(album_entity),ITUNES.HasArtist ,URIRef(artist_entity)))
        g.add((URIRef(artist_entity),ITUNES.HasAlbum ,URIRef(album_entity)))
        g.add((URIRef(artist_entity),ITUNES.Sang ,URIRef(entity_id)))
        g.add((URIRef(entity_id),ITUNES.SungBy ,URIRef(artist_entity)))
        g.add((URIRef(entity_id),ITUNES.HasGenre ,URIRef(Genre_entity)))
        g.add((URIRef(entity_id),ITUNES.PlayTime ,URIRef(Time_entity)))
        g.add((URIRef(entity_id),ITUNES.HasPrice ,URIRef(Price_entity)))
   
    
        #Data Properties
        song_name=Literal(row["Song_Name"],datatype=XSD.string)
        g.add((URIRef(entity_id),ITUNES.Name ,song_name))
        album_name=Literal(row["Album_Name"],datatype=XSD.string)
        g.add((URIRef(album_entity),ITUNES.HasAlbumName ,album_name))
        artist_name=Literal(row["Artist_Name"],datatype=XSD.string)
        g.add((URIRef(artist_entity),ITUNES.HasArtistName ,artist_name))
        album_copyright=Literal(row["Copyright"],datatype=XSD.string)
        g.add((URIRef(album_entity),ITUNES.HasCopyright ,album_copyright))
        song_released_date=Literal(row["Released"],datatype=XSD.string)
        g.add((URIRef(entity_id),ITUNES.ReleasedOn ,song_released_date))
        song_duration=Literal(row["Time"],datatype=XSD.string)
        g.add((URIRef(Time_entity),ITUNES.Duration ,song_duration))
        currency,amount = split_price(row["Price"])
        currency_price=Literal(currency,datatype=XSD.string)
        g.add((URIRef(Price_entity),ITUNES.HasCurrency ,currency_price))
        amount_price=Literal(amount,datatype=XSD.float)
        g.add((URIRef(Price_entity),ITUNES.HasAmount ,amount_price))
        genre_list=row["Genre"].split(",")
        [relations_genre(x,Genre_entity,ITUNES.GenreList) for x in genre_list]
        
        

def main(file):   
    g.parse ('right_ontology.ttl', format='ttl')
    itunes_data=pd.read_csv(file)
    columns_list=['id','label','right_Song_Name','right_Artist_Name','right_Album_Name','right_Genre','right_Price','right_CopyRight','right_Time','right_Released']
    itunes_df=itunes_data[columns_list]
    column_names=['id','label','Song_Name','Artist_Name','Album_Name','Genre','Price','Copyright','Time','Released']
    itunes_df.columns=column_names
    populate_rdf(itunes_df)
    g.serialize('output_file_result_right.ttl',format='ttl')