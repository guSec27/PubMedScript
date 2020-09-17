#!/usr/bin/env python
# coding: utf-8


import urllib
import xmltodict
import xml.etree.ElementTree as ET
import ibm_db

class Action():
    def __init__(self, doi, titolo, autori, pubDate, abstract):
        self.doi = doi
        self.titolo = titolo
        self.autori = autori
        self.pubDate = pubDate
        self.abstract = abstract
        
    def __str__(self):
        return "DOI: %s\nTitolo: %s\nAutori: %s\nData di Pubblicazione: %s\nAbstract: %s\n" % (self.doi, self.titolo, ', '.join(self.autori), self.pubDate, self.abstract)

def getPubMedIDArticles ():
    
    test = "esearch.fcgi?db=pubmed"
    term = "&term=glioblastoma&retmax=100000" #Termini della ricerca
    link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"+test+term
    
    
    print(link)
    
    #url = "webservice"
    s = urllib.request.urlopen(link)
    contents = s.read()
    file = open("export.xml", 'wb')
    file.write(contents)
    file.close()

def PubMedidConverter():
    data_file = 'export.xml'
    tree = ET.parse(data_file)
    root = tree.getroot()
    id_converter = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
    i=0

    articoli = list()

    for child in root.findall("./IdList/Id"):
        i=i+1
        id = child.text
        id_converter1 = id_converter+id+"&retmode=xml"
        #print (id_converter1)

        xml = urllib.request.urlopen(id_converter1).read()
        #data = file.read() file=riga di sopra
        #file.close()

        #data = xmltodict.parse(data)
        xml_tree = ET.fromstring(xml) #è già la root

        for child2 in xml_tree.findall("PubmedArticle"):
            temp_title = ""
            temp_abstract = "" 
            temp_author = ""
            temp_doi = "Mancante"
            temp_pubdate = ""
            autori_vector = []

            for child2_0 in child2.findall("MedlineCitation/Article"):
                for child2_1 in child2_0.findall("ArticleTitle"):
                    #print (child2_1.text)
                    temp_title = child2_1.text
                for child2_2 in child2_0.findall("Abstract/AbstractText"):
                    #print (child2_2.tag, child2_2.attrib, child2_2.t6xt)
                    temp_abstract = child2_2.text
                for child2_3 in child2_0.findall("AuthorList/Author"):
                    #La presente soluzione è concepita nel caso si voglia tenere traccia solo di iniziali del nome e cognome (per intero)
                    #print (child2_3[0].tag, child2_3[0].attrib, child2_3[0].text, child2_3[1].tag, child2_3[1].attrib, child2_3[1].text)
                    #print (child2_3[0].text,child2_3[2].text)
                    #temp_author = child2_3.findall("[@LastName]").text+" "+child2_3.findall("[@Initials]").text+"."
                    path_cognome = child2_3.find("LastName")
                    path_iniziali = child2_3.find("Initials")
                    if (path_cognome != None):
                        if (path_iniziali != None):
                            temp_author = child2_3.find("LastName").text +" "+path_iniziali.text+"."
                        else:
                            temp_author = child2_3.find("LastName").text
                    autori_vector.append(temp_author)
                #print("\n")
            for child2_4 in child2.findall("PubmedData"):
                for child2_5 in child2_4.findall("History/PubMedPubDate/[@PubStatus='entrez']"):
                    temp_pubdate = child2_5[0].text+"-"+child2_5[1].text+"-"+child2_5[2].text
                #for child2_6 in child2_4.findall("ArticleIdList/ArticleId/[@IdType='doi']"):
                    #print(child2_6.text)
                chadfinale = child2_4.find("ArticleIdList/ArticleId/[@IdType='doi']")
                if (chadfinale != None):
                    temp_doi = chadfinale.text
                    print("["+str(i)+"] - ",temp_doi) #Debug dell'articolo recuperato

            #articolo = Articolo (temp_title, autori_vector, temp_abstract)   
            articolo = Articolo (temp_title, autori_vector, temp_pubdate, temp_doi ,temp_abstract)
            articoli.append(articolo)

def ConnectionDB2():
    conn_info = "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-lon02-13.services.eu-gb.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=xxd26106;PWD=s5bzk6p^3s94hght;"
    conn = ibm_db.connect(conn_info, "", "")
    return conn
    
def endConnection (conn):
    ibm_db.close(conn)

def insertArrayDB2 (articoli): #ci va qualcosa come parametro di input
#########In teoria come parametro di input ci va l'intero array ma sarebbe COSA BUONA E ANCHE GIUSTA ficcarci un articolo alla volta
        for articolo in articoli:
            abstract_rep = " "
            titolo_rep = " "

            autori_insert = ', '.join(articolo.autori)
            if (autori_insert != None):
                autori_insert = autori_insert.replace("'", "''")

            if (articolo.titolo != None):
                titolo_temp = articolo.titolo.replace("'", "''")

            if (articolo.abstract != None):
                abstract_temp = articolo.abstract.replace("'", "''")

            insert = ibm_db.exec_immediate(conn, "INSERT INTO articoli (doi, titolo, autori, pubDate, abstract) VALUES ('"+articolo.doi+"', '"+titolo_temp+"', '"+ autori_insert+"', '"+ articolo.pubDate+"', '"+abstract_temp+"')")
            print("["+str(i)+"] - Inserito\n") #DEBUG dell'articolo inserito 

def insertArticleDB2 (articolo):
    abstract_rep = " "
    titolo_rep = " "

    autori_insert = ', '.join(articolo.autori)
    if (autori_insert != None):
        autori_insert = autori_insert.replace("'", "''")

    if (articolo.titolo != None):
        titolo_temp = articolo.titolo.replace("'", "''")

    if (articolo.abstract != None):
        abstract_temp = articolo.abstract.replace("'", "''")

    insert = ibm_db.exec_immediate(conn, "INSERT INTO articoli (doi, titolo, autori, pubDate, abstract) VALUES ('"+articolo.doi+"', '"+titolo_temp+"', '"+ autori_insert+"', '"+ articolo.pubDate+"', '"+abstract_temp+"')")
    print("["+str(i)+"] - Inserito\n") #DEBUG dell'articolo inserito 





