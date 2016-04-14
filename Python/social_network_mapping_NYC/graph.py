"""
This part of the code focuses on the parsing of captions and the following analysis
Consider the situation where lastname includes middle name
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import networkx as nx
import numpy as np
#from igraph import *

"""
Part 2: parsing the captions
"""
caption_df = pd.read_csv('captions_more.csv')
cap_lists = caption_df['captions'].tolist()

name_lists = []      # The list of all names
photo_name_lists = []   # The list of name_list within each graph, need to be used to create the graph edges
pairs_lists = {}

            

    
"""
The following function parse the names in the raw caption soup as a list
"""
def find_name(soup):
    soup_str = str(soup)
    # all the captions between the html tags
    caption = re.search(r'>(.|\n)*?<', soup_str).group(0)[1:-1]
    caplens = len(caption)
    if caplens <= 250:
        return parse_name(caption)
    else:
        return ['na']
    
#potential prefix list
prefixL = ['Dr.', 'Sr.', 'Dr', 'Sr', 'Mayor', 'Senator', 'Chair']

def parse_name(str):
    """
    Given a string, parse out the names following the rules:
    1. simple ones: separated by ',', 'and', 'with'
    2. prefix, provide a prefix list
    3. couple condition (First 1 and Fisrt2 Last)
    4. sentences
    Return: a list of tuples ((First Name, Last Name) for each tuple)
    """
    result_list = []
    #initial separate with ','
    list_one = re.split(',\s{1,3}', str)
    # separate with 'with':
    for text in list_one:
        text = ' ' + text
        text_with = re.split(r'\s+with\s+', text)
        for s in text_with:
            s = ' ' + s
            text_and = re.split(r'\s+and\s+', s)
            for i in text_and:
                #print 'i is:' + i
                name_text = re.split(r'(\s+)', i)
                name_text_1 = re.findall(r'[A-Z]\w+\.*', i)
                #print name_text_1 
                if name_text_1 and (name_text_1[0] in prefixL):
                    #print name_text[0], 'name_text[0]'
                    i = i.replace(name_text_1[0], '')
                    #print 'i is:' + i
                name_text_1 = re.findall(r'[A-Z][A-Za-z\']*\.*', i)   
                if (name_text_1 and len(name_text_1) >=2 and len(name_text_1) <= 4):
                    firstname = name_text_1[0]
                    lastname = ''
                    for j in range(1,len(name_text_1)):
                        lastname = lastname + ' ' + name_text_1[j]
                    result_list.append((firstname, lastname))
                if (name_text_1 and len(name_text_1) ==1):
                # first check if there is a couple
                    couple = re.findall(r'([A-Z]\w+)\s{1,3}and\s{1,3}([A-Z]\w+)\s([A-Z]\w+)', s)
                    if couple:
                        for c in couple:
                            lastname = c[2]
                            first_one = c[0]
                            result_list.append((first_one, lastname))
    return result_list
                         
                
   
"""
Part 3: Analysis using undirected graph to deal with the network
"""     
            
def graph(cap_lists_input):
    """
    input cap_lists
    """
    # Greate the graph
    MG = nx.Graph()
    
    for caption in cap_lists_input:
        list_name = find_name(caption)
        photo_name_lists.append(list_name)
    #for x in list_name:
        # MG.add_node(x)
    #   if not (x in name_lists):
    #       name_lists.append(x)
        if list_name and ('na' not in list_name):
            for item in list_name:
                node_name = item[0] + ' ' + item[1]
                # print node_name
                if not (item in name_lists):
                    name_lists.append(item)
                    MG.add_node(node_name)
            if len(list_name)>=2:
                N = len(list_name)
                for i in range(N-1):
                    for j in range(i + 1, N):
                        name1 = list_name[i][0] + ' ' + list_name[i][1]
                        name2 = list_name[j][0] + ' ' + list_name[j][1]
                        if (name1, name2) in pairs_lists:
                            pairs_lists[(name1, name2)] += 1
                        elif (name2, name1) in pairs_lists: 
                            pairs_lists[(name2, name1)] += 1
                        else: pairs_lists[(name1, name2)] = 1
		                
    #name_lists_df = pd.DataFrame({'name_lists': name_lists})  
    #name_lists_df.to_csv('name_lists.csv')     

    #photo_name_lists_df = pd.DataFrame({'photo_name_lists': photo_name_lists})  
    #photo_name_lists_df.to_csv('photo_name_lists.csv')  

    print '# of pairs is: ', len(pairs_lists)
    # print 'pairs_lists are: ', pairs_lists
    print '# of nodes found: ', len(MG.nodes())
    # print 'Nodes found: ', MG.nodes()
    for (name1, name2) in pairs_lists:
        name_weight = pairs_lists[(name1, name2)]
        MG.add_edge(name1, name2, weight = name_weight)
    print '# of Edges found:', len(MG.edges())
    return MG
    
# degrees (dictionary):
def find_degrees(MG, count):
    """
    MG is the undirected graph
    count is the top candidates
    """
    degrees = MG.degree(weight='weight')
    #print degrees
    top_degree = []
    top_dg_num = []

    degrees_sorted = sorted(degrees, key = degrees.__getitem__, reverse = True)

    for key in degrees_sorted[:count]:
        top_degree.append((key, degrees[key]))
        top_dg_num.append(degrees[key])
        
    top_dg_num_arr = np.array(top_dg_num)
    print 'The mean of degree is: ' , top_dg_num_arr.mean()
    print 'The std of degree is: ' ,top_dg_num_arr.std()
    print 'The min of degree is: ', top_dg_num_arr.min()
    print 'The max of degree is: ', top_dg_num_arr.max()
   
    return top_degree
	
def find_pagerank(MG, count):
    """
    MG is the undirected graph
    count is the top candidates
    """
    pr = nx.pagerank(MG)
    # print pr
    top_node = []
    top_pr_num = []

    pr_sorted = sorted(pr, key = pr.__getitem__, reverse = True)

    for key in pr_sorted[:count]:
        top_node.append((key, pr[key]))
        top_pr_num.append(pr[key])
        
    top_pr_num_arr = np.array(top_pr_num)
    print 'The mean of pagerank is: ' , top_pr_num_arr.mean()
    print 'The std of pagerank is: ' ,top_pr_num_arr.std()
    print 'The min of pagerank is: ', top_pr_num_arr.min()
    print 'The max of pagerank is: ', top_pr_num_arr.max()
   
    return top_node
	
def find_best_friends(count):
    """
    count is the top candidates
    """
    result = []
    freqts = []  # The weights of each eadge
    pairs_sorted = sorted(pairs_lists, key = pairs_lists.__getitem__, reverse = True)
    for key in pairs_sorted[:count]:
        result.append((key, pairs_lists[key]))
        freqts.append(pairs_lists[key])
    freq_arr = np.array(freqts)
    print 'The mean of weights is: ' , freq_arr.mean()
    print 'The std of weights is: ' , freq_arr.std()
    print 'The min of weights is: ', freq_arr.min()
    print 'The max of weights is: ', freq_arr.max()
    return result



def main():
    input = cap_lists
    #print 'input is: '
    #print input
    MG = graph(input)
    count = 100

    top_degrees = find_degrees(MG, count)   
    print top_degrees

    top_pr = find_pagerank(MG, count)
    print top_pr

    best_friends = find_best_friends(count)
    print best_friends

			
	
	
	


if __name__ == '__main__':
    main()