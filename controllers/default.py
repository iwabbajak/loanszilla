# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# INDEX PAGE
@auth.requires_login()
def index():
    # Query Capital Money
    capital_qry =(db.CapAdd_Table.ca_user==auth.user.id)
    capital_view = db(capital_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.ca_datetime)
    # Total Capital calculation
    total_capital = 0
    for capx in capital_view:
        total_capital += capx.ca_amount
    
    # Query Commision Money
    comm_qry =(db.LoanComm_Table.lc_user==auth.user.id)
    comm_view = db(comm_qry).select(db.LoanComm_Table.ALL,orderby=db.LoanComm_Table.lc_datepaid)
    # Total Capital calculation
    total_comm = 0
    other_comm = 0
    for comx in comm_view:
        if comx.lc_comtype =='LC':
            total_comm += comx.lc_amount
        else:
            other_comm +=comx.lc_amount
    
    return dict(auth=auth,total_capital=total_capital,total_comm=total_comm,other_comm=other_comm)

@auth.requires_login()
def wallet():
    # Query Capital Money
    capital_qry =(db.CapAdd_Table.ca_user==auth.user.id)
    capital_view = db(capital_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.ca_datetime)
    # Total Capital calculation
    total_capital = 0
    for capx in capital_view:
        total_capital += capx.ca_amount
    
    # Query Commision Money
    comm_qry =(db.LoanComm_Table.lc_user==auth.user.id)
    comm_view = db(comm_qry).select(db.LoanComm_Table.ALL,orderby=db.LoanComm_Table.lc_datepaid)
    # Total Capital calculation
    total_comm = 0
    other_comm = 0
    for comx in comm_view:
        if comx.lc_comtype =='LC':
            total_comm += comx.lc_amount
        else:
            other_comm +=comx.lc_amount
    
    return dict(auth=auth,total_capital=total_capital,total_comm=total_comm,other_comm=other_comm,
        comm_view=comm_view,capital_view=capital_view)


# MAIN HOME PAGE
@auth.requires_login()
def home():
    #------ Total Money Invested ------
    # Query Capital Funds
    cf_qry =(db.CapAdd_Table.id>=1)
    cf_view = db(cf_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.id)

    tfunds=0
    # Get Total Funds
    for x in cf_view:
        tfunds += x.ca_amount
    
    #------ Total Money Borrowed ------
    # Query Borrowed Funds
    cs_qry =(db.CapSub_Table.id>=1)
    cs_view = db(cs_qry).select(db.CapSub_Table.ALL,orderby=db.CapSub_Table.id)

    tsubs=0
    # Get Total Funds
    for x in cs_view:
        tsubs += x.cs_amount

    #------ Total Incoming Asset from Loan Balanace ------
    # Query Incoming Funds to be Paid
    incoming_qry =(db.Loan_table.id>=1)&(db.Loan_table.lt_remarks=='ONGOING')&((db.Loan_table.lt_status=='RELEASE')|(db.Loan_table.lt_status=='SUCCEEDED'))
    incoming_view = db(incoming_qry).select(db.Loan_table.ALL,orderby=db.Loan_table.id)

    tincom=0
    # Get Total Funds
    for x in incoming_view:
        tincom += x.lt_balance

     #------ Total Money Paid from Loan  ------
    # Query Total Loan Payment Funds
    lp_qry =(db.LoanPay_Table.id>=1)
    lp_view = db(lp_qry).select(db.LoanPay_Table.ALL,orderby=db.LoanPay_Table.id)

    tloanp=0
    # Get Total Funds
    for x in lp_view:
        tloanp += x.lp_amount



    # Latest Loan Display
    latloan_qry =(db.Loan_table.id>=1)
    latloan_view = db(latloan_qry).select(db.Loan_table.ALL,orderby=~db.Loan_table.id,limitby=((0,3)))

    return dict(auth=auth,
    cf_view=cf_view,tfunds=tfunds,
    cs_view=cs_view,tsubs=tsubs,
    latloan_view=latloan_view,tincom=tincom,tloanp=tloanp)












# ACTION PAGE
@auth.requires_login()
def action():
    ugroup = auth.user_groups.values()
    return dict(auth=auth,ugroup=ugroup)




# ---- API (example) -----
@auth.requires_login()  
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
