import os
import sys
import re
from neo4j import GraphDatabase
from difflib import SequenceMatcher

# database setting
uri = 'bolt://localhost:7687'
username = 'neo4j'
password = 'Password123$'
password = "neo4jneo4j"

countries = ["afghanistan", "ålandislands", "albania", "algeria", "americansamoa", "andorra", "angola", "anguilla", "antarctica", "antiguaandbarbuda", "argentina", "armenia", "aruba", "australia", "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados", "belarus", "belgium", "belize", "benin", "bermuda", "bhutan", "bolivia", "bosniaandherzegovina", "botswana", "bouvetisland", "brazil", "britishindianoceanterritory", "bruneidarussalam", "bulgaria", "burkinafaso", "burundi", "cambodia", "cameroon", "canada", "capeverde", "caymanislands", "centralafricanrepublic", "chad", "chile", "china", "christmasisland", "cocos(keeling)islands", "colombia", "comoros", "congo", "congo,thedemocraticrepublicofthe", "cookislands", "costarica", "cotedivoire", "croatia", "cuba", "cyprus", "czechrepublic", "denmark", "djibouti", "dominica", "dominicanrepublic", "ecuador", "egypt", "elsalvador", "equatorialguinea", "eritrea", "estonia", "ethiopia", "falklandislands(malvinas)", "faroeislands", "fiji", "finland", "france", "frenchguiana", "frenchpolynesia", "frenchsouthernterritories", "gabon", "gambia", "georgia", "germany", "ghana", "gibraltar", "greece", "greenland", "grenada", "guadeloupe", "guam", "guatemala", "guernsey", "guinea", "guinea-bissau", "guyana", "haiti", "heardislandandmcdonaldislands", "holysee(vaticancitystate)", "honduras", "hongkong", "hungary", "iceland", "india", "indonesia", "iran,islamicrepublicof", "iraq", "ireland", "isleofman", "israel", "italy", "jamaica", "japan", "jersey", "jordan", "kazakhstan", "kenya", "kiribati", "korea,democraticpeople'srepublicof", "korea,republicof", "kuwait", "kyrgyzstan", "laopeople'sdemocraticrepublic", "latvia", "lebanon", "lesotho", "liberia", "libyanarabjamahiriya", "liechtenstein",
             "lithuania", "luxembourg", "macao", "macedonia,theformeryugoslavrepublicof", "madagascar", "malawi", "malaysia", "maldives", "mali", "malta", "marshallislands", "martinique", "mauritania", "mauritius", "mayotte", "mexico", "micronesia,federatedstatesof", "moldova,republicof", "monaco", "mongolia", "montserrat", "morocco", "mozambique", "myanmar", "namibia", "nauru", "nepal", "netherlands", "netherlandsantilles", "newcaledonia", "newzealand", "nicaragua", "niger", "nigeria", "niue", "norfolkisland", "northernmarianaislands", "norway", "oman", "pakistan", "palau", "palestinianterritory,occupied", "panama", "papuanewguinea", "paraguay", "peru", "philippines", "pitcairn", "poland", "portugal", "puertorico", "qatar", "reunion", "romania", "russianfederation", "rwanda", "sainthelena", "saintkittsandnevis", "saintlucia", "saintpierreandmiquelon", "saintvincentandthegrenadines", "samoa", "sanmarino", "saotomeandprincipe", "saudiarabia", "senegal", "serbiaandmontenegro", "seychelles", "sierraleone", "singapore", "slovakia", "slovenia", "solomonislands", "somalia", "southafrica", "southgeorgiaandthesouthsandwichislands", "spain", "srilanka", "sudan", "surisvalbardandjanmayen", "swaziland", "sweden", "switzerland", "syrianarabrepublic", "taiwan,provinceofchina", "tajikistan", "tanzania,unitedrepublicof", "thailand", "timor-leste", "togo", "tokelau", "tonga", "trinidadandtobago", "tunisia", "turkey", "turkmenistan", "turksandcaicosislands", "tuvalu", "uganda", "ukraine", "unitedarabemirates", "unitedkingdom", "unitedstates", "unitedstatesminoroutlyingislands", "uruguay", "uzbekistan", "vanuatu", "venezuela", "vietnam", "virginislands,british", "virginislands,u.s.", "wallisandfutuna", "westernsahara", "yemen", "zambia", "zimbabwe"]


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def add_strains(tx, strain, key):
    result = tx.run("CREATE (s:Strain {id: $id, sequence: $sequence, type: $type, type_id: $type_id, name: $name, region: $region})", id=strain['id'], name=key, sequence=strain['sequence'], type=strain['type'], type_id=strain['type_id'], region=strain['region'])
    return result


def add_similarity(tx, id1, id2, similarity):
    result = tx.run("MATCH(s1: Strain {id: $id1}), (s2: Strain {id: $id2})CREATE(s1)-[:SEQUENCE_SIMILARITY {value: $similarity}] -> (s2)", id1=id1, id2=id2, similarity=similarity)
    return result


def add_genetic_distance(tx, id1, id2, distance):
    result = tx.run("MATCH(s1: Strain {id: $id1}), (s2: Strain {id: $id2})CREATE(s1)-[:GENETIC_DISTANCE {value: $distance}] -> (s2)", id1=id1, id2=id2, distance=distance)
    return result


def add_hi_titer(tx, id1, id2, hi_titer):
    result = tx.run("MATCH(s1: Strain {id: $id1}), (s2: Strain {id: $id2})CREATE(s1)-[:HI_TITER_VALUE {value: $hi_titer}] -> (s2)", id1=id1, id2=id2, hi_titer=hi_titer)
    return result


def build_strain_obj(strain_name, sequence, strain_id, each_type, type_id):
    splited_name = strain_name.split("/")
    region = splited_name[1]
    for country in countries:
        if country in strain_name.replace("_", "").lower():
            region = country

    # print(region)
    return {
        "sequence": sequence,
        "id": strain_id,
        "type": each_type,
        "type_id": type_id,
        "region": region.upper()
    }


def calculate_genetic_distance(seq1, seq2):
    # Ensure both sequences have the same length
    if len(seq1) != len(seq2):
        raise None

    # Initialize the distance counter
    distance = 0

    # Iterate through each position in the sequences and count differences
    for base1, base2 in zip(seq1, seq2):
        if base1 != base2:
            distance += 1

    return distance

if __name__ == "__main__":
    print("Start converting csv into neo4j")
    sub_types = ["H3N2", "H5N1", "H1N1"]
    strain_objs = {}
    edges = []
    hi_titers = []
    strain_id = 0
    for each_type in sub_types:
        with open('./data/{}_antigenicDataFinal'.format(each_type), 'r') as file:
            file_data = file.read()
            lines = file_data.strip().split('\n')

            distances = []
            sequences = []
            hi_titer_values = []
            
            flag = 0
            last_strain = ""
            for line in lines:
                parts = line.split()
                if len(parts) == 4:
                    continue
                elif len(parts) == 3:
                    strain1, strain2, hi_titer = parts
                    hi_titer_values.append([strain1, strain2, hi_titer])
                elif len(parts) == 2:
                    strain, sequence = parts
                    sequences.append([strain, sequence])
                elif line[0:10:1] != "##########":
                    if flag == 0:
                        last_strain = line
                        flag = 1
                    else:
                        sequences.append([last_strain, line])
                        flag = 0
                        last_strain = ""
                # else:
                #     print("Unexpected data format in line:", line)
                    

            # Now, you have distances and sequences lists containing the respective data.

            # Remove "#" characters from Hi Titer Values and sequences

            hi_titer_values = [[s1.replace("#", ""), s2.replace("#", ""), d] for s1, s2, d in hi_titer_values]
            sequences = [[s.replace("#", ""), seq.replace("#", "")] for s, seq in sequences]
            sequences = [[s.replace(">", ""), seq] for s, seq in sequences]

            # Process sequences
            strained_sequences = []
            for seq in sequences:
                strain, sequence = seq[0], seq[1]
                strain_name = '{}/{}'.format(strain, each_type)
                strain_obj = build_strain_obj(strain_name, sequence, strain_id, each_type, sub_types.index(each_type))
                strain_objs[strain_name] = strain_obj
                strained_sequences.append(strain_obj)
                strain_id += 1

            min_list = []
            for i in range(len(strained_sequences)):
                for j in range(i + 1, len(strained_sequences)):
                    node1 = strained_sequences[i]
                    node2 = strained_sequences[j]
                    distance = calculate_genetic_distance(node1["sequence"], node2["sequence"])
                    similarity = similar(node1["sequence"], node2["sequence"])
                    edges.append([node1["id"], node2["id"], distance, similarity])
                    if float(distance) <= 4:
                        min_list.append(similarity)

            # Process Hi Titer Values
            strain_obj1 = ""
            strain_obj2 = ""
            for row in hi_titer_values:
                strain1, strain2, hi_titer = row
                strain1 = '{}/{}'.format(strain1, each_type)
                strain2 = '{}/{}'.format(strain2, each_type)
                
                if not strain1 in strain_objs:
                    strain_obj1 = build_strain_obj(
                        strain1, '', strain_id, each_type, sub_types.index(each_type))
                    strain_objs[strain1] = strain_obj1
                    strain_id += 1
                else:
                    strain_obj1 = strain_objs[strain1]
                
                if not strain2 in strain_objs:
                    strain_obj2 = build_strain_obj(
                        strain2, '', strain_id, each_type, sub_types.index(each_type))
                    strain_objs[strain2] = strain_obj2
                    strain_id += 1
                else:
                    strain_obj2 = strain_objs[strain2]
                
                hi_titers.append([strain_obj1["id"], strain_obj2["id"], hi_titer])


            match_count = sum(1 for each in min_list if each >= 0.6)

            #print(min_list, each_type, len(min_list), match_count)

            

    # start database related stuffs
    driver = GraphDatabase.driver(uri, auth=(username, password))
    session = driver.session()
    session.run('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r')
    # Drop the index if it exists
    #session.run('DROP INDEX index_7dd86d4')
    # Check if the index already exists
    result = session.run("SHOW INDEXES")
    existing_index = None

    for record in result:
        if 'indexName' in record and record['indexName'] == 'index_7dd86d4':
            existing_index = record

    if not existing_index:
        # The index does not exist, so create it
        session.run('CREATE INDEX FOR (s:Strain) ON (s.id)')
    else:
        print("Index already exists.")

    for key in strain_objs:
        strain = strain_objs.get(key)
        session.execute_write(add_strains, strain, key)
    print(f"Size of Edges : {len(edges)}")
    for row in edges:
        id1, id2, distance, similarity = row
        print(f"Adding hi edge : {row}")
        session.execute_write(add_similarity, id1, id2, similarity)
        session.execute_write(add_genetic_distance, id1, id2, distance)

    print(f"Size of Titers : {len(hi_titers)}")
    for row in hi_titers:
        id1, id2, hi_titer = row
        print(f"Adding hi titer : {row}")
        session.execute_write(add_hi_titer, id1, id2, hi_titer)

    driver.close()
