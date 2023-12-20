# eco-sim
yet another implimentation of [Emergent Economies for Role Playing Games](https://ianparberry.com/pubs/econ.pdf), a simulator for a medieval economy. 


# practical stuff
## installing
- get python3
- activate a venv
- `pip install -r requirements.txt`
## running
- `python3 server.py`
## config
most config is in the code but some important parts are broken out
- **agent price logic** is stored in `/logic`
- **agent trade logic** is stored in `/logic`


# what do we want to achieve
the goal is to check relative prices based on trade connections and abundance. this should let us:
- if a trade line is broken, how are prices affected?
- how many of each given industry are likely to work in a town of N size or resource
- if a given resource becomes more or less scarse, how is population affected?
- in an interconnected trade system, what efffects to cataclysms have? if several large towns are removed, how affected are distant towns?

# order of priority for features
1. [x]simple trade of one product
2. [x]simple trade of one product with conditions (make this if you can, else make that)
3. [x]simple trade of multple products with intermediates (bread, tools, ore, grain)
4. [x]role based agents with self job allocation
5. [ ]allocate specific hard resources to given a given town (ie iron mines or salt deposits) to see price changes in scasity 
6. [ ]allow trade between distant villages

# agent logic
rough outline:
1. consume what i have
2. produce what i can with my resouces
3. place a sell order based on my surplus
4. place a buy order based on my desires
5. choose to pay the outcome of the bidding process for buy and sell
6. if i run out of food, die or change job
7. (stretch goal) if i have ample food, reproduce

important agent logic is stored in the `/logic` folder, mostly.

