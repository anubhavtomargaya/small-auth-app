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

