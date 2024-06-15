import cohere
import requests
import numpy as np
import json
import sys
import os
import argparse
from pyvis.network import Network


cohereAPIkey = os.getenv('COHERE_API_KEY')
if not cohereAPIkey:
    raise ValueError("No Cohere API key found. Please go to https://dashboard.cohere.com/api-keys and then: export COHERE_API_KEY='your_api_key'")
co = cohere.Client(cohereAPIkey)

def searchPaper(title):
    # Return information about the first paper matching the title
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": title,
        "limit": 1,
        "fields": "title,authors,year,abstract"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if len(data) == 0:
        print(response)
        print("Rate limited access to Semantic Scholar API, please wait a moment before trying again")
        return False
    return data["data"][0]

def getReferences(paperID):
    # Return title, authors, abstract, year, contexts, intenets and influence for each referenced paper
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paperID}/references?fields=title,authors,year,contexts,intents,isInfluential,abstract"
    response = requests.get(url)
    data = response.json()
    if len(data) == 0:
        print(response)
        print("Rate limited access to Semantic Scholar API, please wait a moment before trying again")
        return False
    return data["data"]

def getSemanticSimilarity(text1, text2):
    response = co.embed(texts=[text1, text2])
    a, b = response.embeddings
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def getRelevanceScore(mainAbs, references):
    scores = []
    intentsMap = {"methodology":"red", "background":"blue", "result":"green"}
    for ref in references:
        score = 0
        # Frequency count
        citeCount = len(ref["contexts"])
        if citeCount == 0: # If Semantic Scholar API fails to provide contexts 
            citeCount+=1
        score += citeCount

        # Semantic similarity of abstracts
        similarity = getSemanticSimilarity(mainAbs, ref["citedPaper"]["abstract"])
        score *= similarity

        # Influence of paper
        score *= (ref["isInfluential"]*1+1)/2

        # Intent colour mapping
        if len(ref["intents"]) == 0:
            intent = 'gray' # If Semantic Scholar API fails to provide intent 
        else:
            intent = intentsMap[ref["intents"][0]]
        

        scores.append((ref["citedPaper"], score, citeCount, similarity, intent))
    
    # Sort by score
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def drawGraph(rootPaper, scoredReferences):
    net = Network(height="900px", width="100%", notebook=True, bgcolor="#222222", font_color="white")
    net.toggle_physics(True)
    net.force_atlas_2based(
        gravity=-5,      # Increased gravity to spread out nodes more
        central_gravity=0.001,  # Lower central gravity to reduce clustering around the center
        spring_length=200,  # Increased spring length to increase distance between nodes
        spring_strength=0.001  # Adjust spring strength to make it less stiff
    )
    
    # Add root paper as the main node
    net.add_node(rootPaper["title"], label=rootPaper["title"], color="yellow")
    
    # Add citation nodes and edges
    for detail, score, citeCount, similarity, intent in scoredReferences:
        net.add_node(detail["title"], label=detail["title"], value=score*100, color=intent)
        net.add_edge(rootPaper["title"], detail["title"])
        
    return net

def main(paper, dataDir):
    if dataDir == None:
        paperID = paper["paperId"]
        references = getReferences(paperID)
        if not references:
            print("References not found.")
            return None
        print("References found")
        cleanReferences = []
        # Remove any invalid references found by Semantic Scholar
        for ref in references:
            if ref["citedPaper"]["paperId"] != None:
                cleanReferences.append(ref)
        print("References cleaned")
        scoredReferences = getRelevanceScore(paper["abstract"], cleanReferences)
        print("References cleaned")
        print("Attempting to save results...")
        with open(f'{paperID}_scoredReferences.json', 'w', encoding='utf-8') as f:
            json.dump(scoredReferences, f, ensure_ascii=False, indent=4)
        print(f"Saved! {paperID}_scoredReferences.json")
    else:
        print("Attempting to load data...")
        with open(dataDir,'r') as file:
            scoredReferences = json.load(file)
        print("Data loaded")

    rootPaper = {
        "title": paper["title"],
        "year": paper["year"]
    }

    # Create and display the graph
    referenceGraph = drawGraph(rootPaper, scoredReferences)
    referenceGraph.show(f'{paperID}_referenceGraph.html')

# Main script
sys.path.insert(0, './')

parser = argparse.ArgumentParser(description='Arguments for paper reference relevance visualiser')
parser.add_argument('-t', '--title', default='Verifiably Robust Conformal Prediction', type=str, help = 'Title of paper to parse')
parser.add_argument('-d', '--data', type=str, help = 'JSON file of saved citation scores')
args = parser.parse_args()

paperTitle = args.title
dataDir = args.data

paper = searchPaper(paperTitle)
if not paper:
    print("Paper not found.")
else:
    print(f'Paper found: {paper["title"]} {paper["year"]}')
    main(paper, dataDir)