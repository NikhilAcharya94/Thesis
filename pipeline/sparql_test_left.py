# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 21:55:38 2021

@author: Nikhil
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 21:38:43 2020

@author: Nikhil
"""
from rdflib import Graph, Literal, RDF, URIRef,Namespace
from rdflib.namespace import XSD,OWL,RDFS
import pandas as pd
import random
import re
import rdflib
from forex_python.converter import CurrencyRates
from datetime import datetime
import dateutil.parser as parser
import math
c = CurrencyRates()
c_rates=c.get_rates('EUR')
g = rdflib.Graph()
ITUNES = Namespace("http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#")
minutes_entity= "http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#"+"Minute"
seconds_entity= "http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#"+"Seconds"
Time_class= "http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#"+"Time"
duration_class="http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#"+"Duration"

def string_acronym_populate(artist_name_uri,artist_alias_uri):
    for alias in artist_alias_uri:
        query_v="PREFIX ITUNES: <http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#>  SELECT ?song WHERE { <"+alias+"> ITUNES:Sang ?song.}"
        qres =g.query(query_v)
        for row in qres:
            g.add((URIRef(artist_name_uri),ITUNES.Sang, row["song"]))
            g.remove((URIRef(alias),ITUNES.Sang, row["song"])),

def string_acronym_match(df):
    album_uris= df['album_uri'].unique()
    for album in album_uris:
        df_album=df[(df.album_uri == album)]
        artist_uri_l=list(df_album[(df_album.counts == df_album.counts.max())].artist_uri)
        if(len(artist_uri_l)>1):
            artist_uri_l=artist_uri_l[0]
        else:
            artist_uri_l=str(artist_uri_l)
            artist_uri_l=artist_uri_l.strip("[]")
            artist_uri_l=artist_uri_l.replace("'","")
        artist_alias_l=list(df_album[(df_album.artist_uri != artist_uri_l)].artist_uri)
        string_acronym_populate(artist_uri_l,artist_alias_l)
        

def resolve_conversion_rate():
    qres_conversion = g.query(
    """ PREFIX ITUNES: <http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#> 
        SELECT ?price ?currency ?amount
       WHERE {
          ?price ITUNES:HasCurrency ?currency .
          ?price ITUNES:HasAmount ?amount .
          }
       """)
    
    for row in qres_conversion:
        song_price=str(row.asdict()["price"].toPython())
        song_amount=float(row.asdict()["amount"].toPython())
        song_currency=str(row.asdict()["currency"].toPython())
        if(str(row.asdict()["currency"].toPython())=="EUR" or str(row.asdict()["currency"].toPython())=="EURO"):
            currency_price_new=Literal("$",datatype=XSD.string)
            g.remove((URIRef(song_price), ITUNES.HasCurrency, row["currency"]))
            g.add((URIRef(song_price), ITUNES.HasCurrency, currency_price_new))
            song_amount_coverted=song_amount*c_rates["USD"]
            price_amount_new=Literal(song_amount_coverted,datatype=XSD.float)
            g.remove((URIRef(song_price), ITUNES.HasAmount, row["amount"]))
            g.add((URIRef(song_price), ITUNES.HasAmount, price_amount_new))
        elif(str(row.asdict()["currency"].toPython())=="¢"):
            currency_price_new=Literal("$",datatype=XSD.string)
            g.remove((URIRef(song_price), ITUNES.HasCurrency, row["currency"]))
            g.add((URIRef(song_price), ITUNES.HasCurrency, currency_price_new))
            song_amount_coverted=song_amount/100
            price_amount_new=Literal(song_amount_coverted,datatype=XSD.float)
            g.remove((URIRef(song_price), ITUNES.HasAmount, row["amount"]))
            g.add((URIRef(song_price), ITUNES.HasAmount, price_amount_new))
            
            
def resolve_time_duration():
    qres_time_duration = g.query(
    """ PREFIX ITUNES: <http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#> 
        SELECT ?time_id ?duration
       WHERE {
          ?time_id ITUNES:Duration ?duration .
          }
       """)
    for row in qres_time_duration:
        duration_song=str(row.asdict()["duration"].toPython())
        time_id=str(row.asdict()["time_id"].toPython())
        time_split=re.split(r"[^a-zA-Z0-9\s]",duration_song)
        if(time_split[0]==""):
            time_split[0]="0"
        if(time_split[1]==""):
            time_split[1]="0"
        minute_song=Literal(float(time_split[0]),datatype=XSD.double)
        second_song=Literal(float(time_split[1]),datatype=XSD.double)
        g.remove((URIRef(time_id), ITUNES.Duration, row["duration"]))
        g.add((URIRef(time_id), ITUNES.Minute, minute_song))
        g.add((URIRef(time_id), ITUNES.Seconds, second_song))
        
        
def resolve_date_conflict():
      qres_song_date = g.query(
      """ PREFIX ITUNES: <http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#> 
          SELECT ?song_name ?date ?song
          WHERE {
            ?song ITUNES:Name ?song_name .
            ?song ITUNES:ReleasedOn ?date .
               }
           """)
      for row in qres_song_date:
          date_song_str=str(row.asdict()["date"].toPython())
          song_id=str(row.asdict()["song"].toPython())
          if(date_song_str=="nan" or date_song_str=="NaT"):
              date_song_str="" 
          else:
              date_song=str(parser.parse(date_song_str))
          date_song_literal=Literal(date_song,datatype=XSD.string)
          g.remove((URIRef(song_id), ITUNES.ReleasedOn, row["date"]))
          g.add((URIRef(song_id), ITUNES.ReleasedOn, date_song_literal))
          #date_song=datetime.strptime(date_song_str, '%d/%m/%y')
          #print(date_song)

def resolve_acronym_conflict():
    qres_conversion_new =g.query(
      """ PREFIX ITUNES: <http://www.semanticweb.org/nacharya/ontologies/2020/11/Itunes-Ontology#> 
          SELECT ?artist ?album ?song
          WHERE {
            ?song  ITUNES:SungBy  ?artist .
            ?song  ITUNES:IsFrom  ?album .
            ?album ITUNES:HasArtist ?artist .
            ?artist ITUNES:HasArtistName ?artist_name .
            ?album ITUNES:HasAlbumName ?album_name .
            }
           """)
    album_name_l=[]
    artist_name_l=[]
    song_l=[]
    for row in qres_conversion_new:
        album_name_l.append(str(row.asdict()["album"].toPython()))
        artist_name_l.append(str(row.asdict()["artist"].toPython()))
        song_l.append(str(row.asdict()["song"].toPython()))

    column_names = ["album_uri", "artist_uri","song"]
    df = pd.DataFrame(columns = column_names)
    df['album_uri']=album_name_l
    df['artist_uri']=artist_name_l
    df['song_uri']=song_l
    count_unique_artists=df.groupby('album_uri').artist_uri.nunique()
    dupe_artists=list(count_unique_artists[count_unique_artists>1].index)
    df=df[df['album_uri'].isin(dupe_artists)]
    df=df.groupby(['artist_uri', 'album_uri']).size().reset_index(name='counts')
    string_acronym_match(df)
    
    
def main():      

    g.parse ('output_file_result.ttl', format='ttl')
    g.add((URIRef(minutes_entity), RDF.type ,OWL.DatatypeProperty))
    g.add((URIRef(minutes_entity), RDFS.domain ,URIRef(Time_class)))
    g.add((URIRef(minutes_entity), RDFS.range ,XSD.double))
    g.add((URIRef(seconds_entity), RDF.type ,OWL.DatatypeProperty))
    g.add((URIRef(seconds_entity), RDFS.domain ,URIRef(Time_class)))
    g.add((URIRef(seconds_entity), RDFS.range ,XSD.double))
    g.serialize('output_file_result.ttl',format='ttl')
    #g = rdflib.Graph()
    g.parse ('output_file_result.ttl', format='ttl')
    resolve_conversion_rate()
    resolve_time_duration()
    resolve_date_conflict()
    resolve_acronym_conflict()
    g.remove((URIRef(duration_class), RDF.type ,OWL.DataTypeProperty))
    g.serialize('output_file_conflicts.ttl',format='ttl')        