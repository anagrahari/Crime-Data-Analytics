Goals\Deliverables:

This is the final project for CSE 564 (Visualization) course where our aim is to develop an Interactive web visualization which will be helpful to gain insight about the trends; increase/decrease in number of crimes in US during recent years. Our final goal will be to deliver the following -

Show the low, medium and high crime density areas on the US map.
Provide two modes of analysis - city-wise and state-wise.
Provide user interaction so that they can set the severity of different type of crimes.
Provide user interaction to increase and decrease a particular type of crime to filter the areas on the map.
Draw plots and graphs to compare and correlate among interesting features of the crime data.


Methodology:
We have used MongoDB to store the data from CSV file to database.
We have used python (PyCharm IDE) for data cleaning and processing.
Server:  Our server runs on localhost through python Flask framework.
Client: Our Client side implementation is on javascript, html and d3.js libraries.
We will use different python libraries for our data analysis and other plottings.


Steps to run project:

1. First you need to install the MongoDB in your system. Download MongoDB from https://www.mongodb.com/download-center#community and install it on your system. (Watch the tutorial videos available at - https://www.youtube.com/watch?v=1uFY60CESlM&list=PL6gx4Cwl9DGDQ5DrbIl20Zu9hx1IjeVhO&index=1)

2. Add the path of the 'bin' folder of installed MongoDB software.

3. Make a directory in your C drive by using the command mkdir \data\db in cmd.

4. Now follow these steps to start the MongoDB server -
- Open cmd.
- execute command -> mongod. This should start your server.
- Open another cmd window and execute command -> mongo. This should show a cursor in the cmd 

5. Now we need to integrate the MongoDB in PyCharm. We need to add the Mongo plugin to the PyCharm. To install the plugin, go to File -> Settings -> Plugins, and search for Mongo Plugin and install it. Once installed you will be able to see the Mongo Explorer (on the right side) in your PyCharm IDE.

6. Click on the settings button in the Mongo Explorer and goto Manage Servers. Give path to Mongo executable as the path to the 'bin' folder of your installed MongoDB software. You can check if the executable is fine by clicking on the 'Test' button.

7. Now we need to add a server configuration. Click on the "+" button and give a label to your server. Leave the other settings unchanged and hit "OK". Once you click OK, you will we able to see the localhost server in the Mongo Explorer.

8. To connect to the server, first start your server (if it is not running already) by opening cmd and executing -> mongod. Now right click on the localhost and click on 'Connect to this server'. Hit the console shell button on the top of Mongo Explorer to open the Mongo console shell where you can start executing the DB commands.

9. Now go to the location where the .csv file is present. Open cmd at that location and execute command -

mongoimport -d crime_db -c crime_data_state --type csv --file Crime_Data_State.csv --headerline
mongoimport -d crime_db -c crime_data_county --type csv --file Crime_Data_County.csv --headerline
mongoimport -d crime_db -c crime_report --type csv --file Crime_Reports.csv --headerline
mongoimport -d crime_db -c crime_report --type csv --file Crime_Reports_Decimated.csv --headerline

This will create a database named 'uselections' and a collection named 'election' and insert all the data from the csv file to this collection.

10. Go to the Mongo Shell in PyCharm and execute the following commands to see if you are able to fetch the data properly

use uselections
show collections
db.election.findOne()
db.election.find()
db.election.find({}, {state:1, state_abbreviation:1, votes:1, _id:0})

11. Run the main.py file and open http://localhost:5050/ on your browser.