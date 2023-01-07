from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

import os
import datetime
import time

# os.environ["TZ"] = "Asia/Manila"
# time.tzset()

#os.environ["TZ"] = "Asia/Singapore"
#time.tzset()
now = datetime.datetime.today()

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------

auth.settings.extra_fields['auth_user'] = [
Field('auth_gcashno','string', label='Gcash Number',required=True),
Field('auth_gcashname','string',label='Gcash Name',required=True),
Field('auth_usercontact','string',label='Contact Number'),
]

auth.define_tables(username=True, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)


# ADDITIONAL TABLES DATABASE
#########################################################################
## Disable BEFORE firstrun until created FIRST USER and USER GROUP
#########################################################################
## Purpose is make all user member to a default group with group_id #1
auth.settings.create_user_groups = False        ##Disable if first run creating first user and blank groups
auth.settings.everybody_group_id = 1              ##Disable if first run creating first user and blank groups
auth.settings.login_next = URL('default', 'home') ##This is the page will be displayed after login


# ---------------------------------------- CAPITAL TABLES ----------------------------------------
##Capital Add Table
db.define_table('CapAdd_Table',
Field('ca_user','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('ca_amount','double',label='Amount',notnull=True,required=True,writable=True),
Field('ca_datetime',label = 'Transaction Time',notnull=True,required=True,writable=False,default=now,editable=False),
)


##Monthly Total Table
db.define_table('MonthTotal_Table',
Field('mt_amount','double',label='Amount',notnull=True,required=True,writable=True),
Field('mt_datetime',label = 'Transaction Time',notnull=True,required=True,writable=False,default=now,editable=False),
)


# ---------------------------------------- LOAN TABLES ----------------------------------------
##Borrowers Table
db.define_table('Borrowers_table',
Field('bt_firstname','string',label='First Name',notnull=True,required=True,writable=True),
Field('bt_lastname','string',label='Last Name',notnull=True,required=True,writable=True),
Field('bt_contact','string',label='Contact Number'),
Field('bt_creditstatus','string',label='Credit Status',required=True,requires=IS_IN_SET(['GOOD','DELAYED']),default='GOOD'),
Field('bt_creditscore','double',label='Credit Score',default=50),
Field('bt_remarks','string',label='Remarks'),
Field('bt_addedby','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
)

##Term Table
db.define_table('Term_table',
Field('tt_term','integer',label='Term',notnull=True,required=True,writable=True),
)

##Interest Table
db.define_table('Interest_table',
Field('it_interest','double',label='Interest',notnull=True,required=True,writable=True),
)

## Loan Table
db.define_table('Loan_table',
Field('lt_amount','double',label='Loan Amount',default=2000,required=True,notnull=True,writable=True),
Field('lt_borrower','reference Borrowers_table',required=True,requires=IS_IN_DB(db,db.Borrowers_table.id,'%(bt_firstname)s - %(bt_lastname)s')),
Field('lt_reason','string',label='Reason'),
Field('lt_comker','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lt_amountapprove','double',label='Loan Amount',default=2000,required=True,notnull=True,writable=True),
Field('lt_interest','reference Interest_table',label='Interest',required=True,requires=IS_IN_DB(db,db.Interest_table.id,'%(it_interest)s')),
Field('lt_interestamount','double',label='Interest Amount',notnull=True,writable=True),
Field('lt_term','reference Term_table',required=True,requires=IS_IN_DB(db,db.Term_table.id,'%(tt_term)s')),
Field('lt_balance','double',label='Loan Balance',required=True,notnull=True,writable=True),
Field('lt_approveby','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lt_dateapproved',label = 'Date Approved',notnull=True,required=True,writable=False,default=now,editable=False),
Field('lt_gcashreference','string',label='GCash Reference'),
Field('lt_daterelease',label = 'Date Release',notnull=True,required=True,writable=False,default=now,editable=False),
Field('lt_releaseby','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lt_processingfee','string',label='Processing Fee'),
Field('lt_remarks','string',label='Remarks',required=True,requires=IS_IN_SET(['PAID','ONGOING']),default='ONGOING'),
Field('lt_status','string',label='Status',required=True,requires=IS_IN_SET(['INPROCESS','APPROVED','RELEASE','SUCCEEDED','REJECTED','FULLY PAID']),default='INPROCESS'),
Field('lt_additioninfo','string',label='Additional Info'),
Field('lt_amountrelease','double',label='Amount Release',required=True,notnull=True,writable=True,default=0),
)


##Capital Sub Table
db.define_table('CapSub_Table',
Field('cs_user','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('cs_amount','double',label='Amount',notnull=True,required=True,writable=True),
Field('cs_reaseon','string',label='Reason'),
Field('cs_datetime',label = 'Transaction Time',notnull=True,required=True,writable=False,default=now,editable=False),
Field('cs_refloan','reference Loan_table',required=True,requires=IS_IN_DB(db,db.Loan_table.id,'Ref# %(id)s')),
)

# ---------------------------------------- LOAN PAYMENT TRACKING ----------------------------------------
## Loan Payment Table
db.define_table('LoanPay_Table',
Field('lp_loan','reference Loan_table',required=True,requires=IS_IN_DB(db,db.Loan_table.id)),
Field('lp_amount','double',label='Loan Payment',required=True),
Field('lp_datepaid',label = 'Date Paid',notnull=True,required=True,writable=False,default=now,editable=False),
Field('lp_processby','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lp_gcashreference','string',label='GCash Reference'),
)


# ---------------------------------------- LOAN COMMISION TRACKING ----------------------------------------
## Loan Commision Table
db.define_table('LoanComm_Table',
Field('lc_loan','reference Loan_table',required=True,requires=IS_IN_DB(db,db.Loan_table.id)),
Field('lc_amount','double',label='Loan Payment',required=True),
Field('lc_datepaid',label = 'Date Paid',notnull=True,required=True,writable=False,default=now,editable=False),
Field('lc_user','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lc_percentage','double',label='Percentage',required=True),
Field('lc_processby','reference auth_user',required=True,requires=IS_IN_DB(db,db.auth_user.id,'%(first_name)s - %(last_name)s')),
Field('lc_comtype','string',label='Type',required=True,requires=IS_IN_SET(['LC','CC','AC']),default='LC'),
)

# ---------------------------------------- NOTICE BOARD TABLE ----------------------------------------
## Notice Message Table
db.define_table('Notice_Table',
Field('nt_title','string',label='Notice Title'),
Field('nt_message','string',label='Notice Message'),
)