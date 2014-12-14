# Macrostrat API
The API for SCIENCE

### About
The Macrostrat API provides diverse macrostratigraphic and geologic data in a concise, queryable format.

### Install
````
git clone https://github.com/UW-Macrostrat/macrostrat-api.git
cd macrostrat-api
npm install
npm start
````
You will need to update rename ````vx/credentials.example.js```` to ````vx/credentials.js```` and input your credentials. The API runs on port ````5000```` by default. 

### Tests
````
npm test
````

### Organization
Each version of the API functions as a self-contained module, and therefore has its own ````package.json```` and dependencies. 

### Contributors
[John J Czaplewski](https://github.com/jczaplew) and [Shanan E Peters](http://strata.geoglogy.wisc.edu)

### License
CC0 for all code unique to this API.