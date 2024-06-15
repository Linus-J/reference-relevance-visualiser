# Paper Reference Relevance Visualisation

Simply provide the title to any research paper to visualise all referenced papers scaled by relevance in an interactive network.

<img src="https://github.com/Linus-J/reference-relevance-visualiser/blob/master/example.png" alt="Example" width="800"/>

Each cited paper is assigned a score based on it's relevance to the root paper. This score determines the size of each node in the network.

The score is calculated with respect to the:
- Number of citations of a given paper in the root paper.
- Semantic similarity of the given and root paper's abstracts.
- Influence of a given paper to the root paper.

Semantic similarity is computed using Cohere's [embedding function](https://docs.cohere.com/docs/embeddings) by computing the similarity between the embedded version of both abstracts.

Influence is a boolean variable determined by Semantic Scholar's [isInfluential variable](https://www.semanticscholar.org/faq#influential-citations).

The colour of each node is determined by the [intent](https://www.semanticscholar.org/faq/citation-intent) of each paper given by the Semantic Scholar API.
- Background = Blue
- Method = Red
- Result = Green
- Root = Yellow
- None = Grey

#### Set environment variable for Cohere

Copy your Cohere API key from [here](https://dashboard.cohere.com/api-keys). 

Replace 'your_api_key' with copied key:

    export COHERE_API_KEY='your_api_key'

#### Install requirements

    pip install -r requirements.txt

#### Run main.py with your desried paper title

    python main.py -t "PAPER TITLE HERE"

#### To just run with the stored JSON file

    python main.py -d PATH_TO_FILE
