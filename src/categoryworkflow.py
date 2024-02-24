
from peewee import fn,SQL
from models import VPA,Transactions

from models import db

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.info)

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

def getTxnsForQuery(query):
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
            tags.append('UNKWN')
    # print(tags)
    return [(x,y) for x,y in (zip(vpas,tags))]
        


# vpas = getTxnsForQuery(getLastNdaysReport())
# # print(vpas)
# print(goThroughVPAs(vpas))
# # getTopVpasByAmount()
# getTopVPAs()
# print(goThroughVPAs(getRecurringVPAs()))
# print(goThroughVPAs(getTopVpasByAmount()))

