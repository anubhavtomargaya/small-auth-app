## small-auth-app
Goal of this project is to provide a api over the gmail fetching application along with experimenting an authorisation flow with google auth. 

## precursor 
Before this project was started, the way to fetch & transform emails from gmail was written as an ETL pipeline.
For this I used a node/pipeline framework.

## development
 later these nodes turned into workflows shedding off unnecessary objects in the code. Everything became functional. Workflows could be called from a main function or through a flask endpoint.

 It was accessible from outside but there was no way to take the user credentials and retrieve token, in fact I was manually putting a token.pickle file in my project via triggering a python script that opened my browser and took credentials from there. I was too lazy to update it as it was mostly getting updated automatically while I was developing and pushing. When I deployed the code (in AWS EC2) It worked for only few days. 
 Had to refresh token and also tried working other ways to authenticate the user (fetch token from a separate auth service) but had to change the code a lot. Added flask session and google auth blueprint that works with the google apis to authenticate. In this the major task was to understand the google auth API (with the scary documentation, but ended well, credit to whatever struggle I did with the Gmail & Youtube API) and implement in the flow to fetch from gmail as it was written in different ways. Everytime I came back to this project with 2-3 months gap I found it tricker.

 Then I also had to run it as a scheduler. So it became a single service, slowly it got cleaner.
 Didnt need to store anything in database as the web api was directly feeding a frontend we got rid of the db methods(hence the small auth app)

## function
Contains a flask api, some html files for whatever ui we have, workflows with functions for everything (and also classes) <:._.:>
auth.py contains the google auth stuff. files in src are some utilities.
json files store some samples.
- run main to start server (no wsgi implemented)
- /google/login to login opens a button to login.
- /fetch extracts & transforms the data and returns in 'transaction' schema
- some scheduler was running this and pushing to postgres and we put that behind a simple visualisation tool for our charts.


## oh!
 At the start I put a lot of work in implementing a ORM for this,( and I did) but it was not a great success at that time of application as I see now. But peewee is a great library to understand ORMs and I have left the basic code of that implementation just for later. SQLAlchemy is the industry standard ORM and better choice for many reasons in future projects but I have not used it in my projects yet. simply because I havent been able to go through the documentation whenever I have tried, and I work with databases more for analytical queries than transactional. I had a lot of fun using Mongo (and pymongo client) for a project, so if I am using that in future I dont need ORMs there either.

 There was a lot of reasons to not use ORMs and then I started using pydantic as well which solved the problem of dirty validation code in my application. which is just what I needed anyway, so no ORM currently but wait.

 I wanted to understand the service oriented architecture (and all other architectures) and it never made sense to me as I had done very little web development, that too pre react era. And I was a data engineer(with electronics head).

 Flask was the obvious choice to learn to make a web service in python. Its supposed to be very neat abstraction of all HTTP and WSGI bits that actuals to the boiler plate code for writing a web service. If the goal of the web-service is to expose an endpoint that says hello, it is shown in hundereds of web pages of flask tutorials. some complex applications are built in flask with flask-app-builder. 

 To create a 

 
 