# FLOW


## FETCH
check for user's details in db.
take input from the logged in user.
    A. User coming first time
        i. Auto fetch the chosen biz emails, i.e. banks, online shopping etc
        ii. Take an email as input to search for. defaults to alerts@hdfcbank
    common inputs: time range

    B. User coming back 
        i. sync from last synced. Use the historyId saved during last sync
        ii. Manual as before

Get the email from inbox 
- formulate the query for fetch service
- get the raw results > extract bs64 and save into db
- convert into html > extract into transaction schema and insert into db
- maintain a table that stores metadata of the operation for each 'session' which is rep by a unique query
    Compare the count of record in each stage to make sure nothing lost.
    Ability to see the original email of a record in transaction


## 26 feb
Test the functionality to
- get token and store in flask session -> or store in db
- fetch the user details and log the user in db
- ask the user for input : default input hdfc alerts email -> save to db with user
- fetch emails for last n days, limited to a quarter -> save to raw transactions table
- **keep a count of messages returned by keeping a session for the "FETCH" -> fetch_logs table to store the session id, number of records returned in each STAGE
-- MAILBOX end
- service to take bs64 data -> decode (to html) -> identify the "significant" part in terms of html tag
    this is currently a logic based on config to choose the nth child elements or something to get the relevant <p> tag.

- extract the keys: date, amount, tovpa, ref no. from the data using regex -> store in transaction table
-- PARSER END
- service to guess the tag > 
    i. attack the vpa > classify it using any means possible > cut the letters match with all the words and make a sense > use the number maybe its a friend? > or just drop it and beg the user for an input
    ii. snatch the time away, rip it apart along with the amount > put it amongst its peers > and it's masters > find a way to mark this as a habit > a routine that many may follow? > or many in the group they belong to ?
    iii. use any available data with you, find if you have labelled something similar and throw it back being a little cheeky
collect the tags from all and rank them > return a list on top n.
- service to take the input from begging the user to label something

--GPT AGENT
- identify the "relevant" html <p> tag or <tables> that represent data
- prompt to generate what tags can be extracted from the identified "r" tag
- build the regex to extract the values for the identified available gold keys in the heap 
    this can be passed as default for now : credit or upi, debited amount, to, date 
    as the default alerts email is being considered
- let the gpt agent be for later.



