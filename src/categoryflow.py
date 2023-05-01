
from peewee import fn,SQL
from models import VPA,Transactions

from models import db

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def getLastNdaysReport(n=30):
    """ defaults: 30 days"""

    q_ = f"""
    SELECT to_vpa,
    count(*) as "count" ,
    CAST(sum(amount_debited) AS INTEGER) as "amount",
    CAST(sum(amount_debited)/count(*) as INTEGER) as "amtPtxn"

    FROM transactions_02 
    WHERE to_vpa IS NOT NULL
    and date > CURRENT_DATE - INTERVAL '{n} days'
    GROUP BY 1
    ORDER BY 3 desc
    
    LIMIT 90;
    """
    return q_

def getVPAsForQuery(query):
    cursor = db.execute_sql(query)
    # columns = [x.name for x in cursor.description]
    # print(columns)
    # rows = [row for row in cursor.fetchall()]
    # rows = [(row[0],row[4],row[1],row[2],row[5]) for row in cursor.fetchall()]
    # print([x for x in zip(rows)])
    result_vpas=[(str(row[0]).split('@')[0]) for row in cursor.fetchall()]
    # print(result_vpas)
    return result_vpas



def getTopVpasByCount():
    q = Transactions.select(Transactions.to_vpa,fn.COUNT(Transactions.txn_id).alias('count')).group_by(Transactions.to_vpa).order_by(SQL('count').desc()).limit(20)
    result= [(str(row.to_vpa).split('@')[0]) for row in q]
    
    # result= [row.to_vpa for row in q]
    # print(result)
    return result
#get big txns from all the data for a user that  dont have a category
def getTopVpasByAmount():
    q = Transactions.select(Transactions.to_vpa,fn.SUM(Transactions.amount_debited).alias('amount')).group_by(Transactions.to_vpa).order_by(SQL('amount').desc()).limit(20)
    result= [(str(row.to_vpa).split('@')[0]) for row in q]

    # print(result)
    return result


def getRecurringVPAs():
    q_monthly = """
    SELECT to_vpa,
    count(*) as "count" ,
    CAST(sum(amount_debited) AS INTEGER) as "amount",
    (sum(amount_debited)/count(*)) as "amtPtxn", 
    cast((cast(count(*)/count(distinct date_trunc('month',date)) as decimal(5,2))) as decimal(3,2)) as "txnPmonth",
    count(distinct date_trunc('month',date)) as "distinctMonths"
    FROM transactions_02 
    WHERE to_vpa IS NOT NULL
    GROUP BY 1
    HAVING count(*) > 1
    AND cast((cast(count(distinct date_trunc('month',date)) as decimal(5,2))/count(*)) as decimal(3,2)) =1
    ORDER BY 3 desc
    
    LIMIT 20;
"""
    q_weekly = """
    SELECT to_vpa, 
    count(*) as "count",
    CAST(sum(amount_debited) AS INTEGER) as "amount",
    (sum(amount_debited)/count(*)) as "amtPtxn", 
    cast((cast(count(*)/count(distinct date_trunc('week',date)) as decimal(5,2))) as decimal(3,2)) as "txnPWeek",
    count(distinct date_trunc('week',date)) as "distinctWeeks"
    FROM transactions_02 
    WHERE to_vpa IS NOT NULL
    GROUP BY 1
    ORDER by 5 desc
    
    LIMIT 20;
"""
    cursor = db.execute_sql(q_monthly)
    # columns = [x.name for x in cursor.description]
    # print(columns)
    # rows = [row for row in cursor.fetchall()]
    # rows = [(row[0],row[4],row[1],row[2],row[5]) for row in cursor.fetchall()]
    # print([x for x in zip(rows)])
    result_vpas=[(str(row[0]).split('@')[0]) for row in cursor.fetchall()]
    # print(result_vpas)
    return result_vpas

def getTopVPAs():
    q = """
        SELECT to_vpa,count(*) as "count" ,CAST(sum(amount_debited) AS INTEGER) as "amount",(sum(amount_debited)/count(*)) as "amtPtxn", cast((cast(count(distinct date_trunc('month',date)) as decimal(5,2))/count(*)) as decimal(3,2)) as "txnPmonth",count(distinct date_trunc('month',date)) as "distinctMonths"
        FROM transactions_02 
        WHERE to_vpa IS NOT NULL 
        GROUP BY 1
        HAVING count(*) >2
        ORDER BY 3 desc
       
        LIMIT 20;
    """
    cursor = db.execute_sql(q)
    # columns = [x.name for x in cursor.description]
    # print(columns)
    # rows = [row for row in cursor.fetchall()]
    # rows = [(row[0],row[4],row[1],row[2],row[5]) for row in cursor.fetchall()]
    # print([x for x in zip(rows)])
    result_vpas=[(str(row[0]).split('@')[0]) for row in cursor.fetchall()]
    print(result_vpas)
    return result_vpas

def goThroughVPAs(vpas):
    tags=[]
    for item in vpas:
        if item in ('8815224653','9993301468','imanubhav18','credclub','zerodhabroking','cred.ccbp'):
            tags.append('SELF')
        elif item in ('murlikumar4u','deepanshujangid21-1','9945466900'):
            tags.append('RENT')
        elif  'swiggy' in item or 'zomato' in item :

            tags.append('FOOD')
        elif 'airtel' in item or 'bill' in item:
            tags.append('BILLS')
        else:
            tags.append(None)
    # print(tags)
    return [(x,y) for x,y in (zip(vpas,tags))]
        
##Insert the looped VPAs with category into DB. WIll be used later

# vpas = getVPAsForQuery(getLastNdaysReport())
# # print(vpas)
# data = goThroughVPAs(vpas)
# print(VPA.insert_many(data, fields=[VPA.vpa_user, VPA.category]).execute())


def getVPAMapping():
    selectVPA = """
    SELECT vpa_user,category FROM vpa
    WHERE category is not null
    """

    
    cursor = db.execute_sql(selectVPA)
    result_vpas=[(row[0],row[1]) for row in cursor.fetchall()]
    return result_vpas


def getTransactionsView(n=30):
    q_ = f"""
        with txns as (
            select "msgId" ,"date",split_part(to_vpa,'@',1) as "user_vpa" ,"amount_debited" from transactions_02 
            where "date" > current_date - interval '{n} days')
            select "msgId" ,"date",v.vpa_user,v.category,amount_debited  from txns t left join vpa v on t.user_vpa =v.vpa_user 
            order by date desc"""
    cursor = db.execute_sql(q_)
    r = [row for row in cursor.fetchall()]
    return r
    
#get uncategorised VPAs #1
def getUncategorisedTxns():
    q_ = f"""with 
                txns as (
                    select "msgId" ,"date",split_part(to_vpa,'@',1) as "user_vpa" ,"amount_debited" from transactions_02 
                    where "date" > current_date - interval '30 days'),
                vw as (
                    select "msgId" ,"date",v.vpa_user,v.category,amount_debited
                    from txns t left join vpa v 
                    on t.user_vpa =v.vpa_user 
                    where V.category is NULL
                    )
                select vpa_user,
                sum(amount_debited)  as "amount",
                count(amount_debited)  as "count",
                min(date) as "earliestdttm",
                max(date) as "latestdttm"
                from vw
                group by 1
                order by 3 desc"""
    #returns total amount spent, number of txns, max-min date of the txns for each VPA
    
    return getVPAsForQuery(q_)


#update category of a VPA, args: vpa, label, category, tags
def UpdateVPACategory(vpa_user):
    pass




# =========test=========
# print(getUncategorisedTxns())
# print(getVPAMapping())
# print(getTransactionsView())
# from models import TransactionsView
# rw = getTransactionsView()[0]
# md = TransactionsView()
# md.msgId=rw[0]
# print(md.msgId)
# print(goThroughVPAs(getTopVpasByAmount()))
# getTopVPAs()
# print(goThroughVPAs(getRecurringVPAs()))
# print(goThroughVPAs(getTopVpasByAmount()))

