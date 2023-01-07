# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ALL CAPITAL PAGE
@auth.requires_login()
def allcapital():
    # Query Capital Money
    capital_qry =(db.CapAdd_Table.id>=1)
    capital_view = db(capital_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.ca_datetime)
    # Total Capital calculation
    total_capital = 0
    for capx in capital_view:
        total_capital += capx.ca_amount
    
    return dict(auth=auth,total_capital=total_capital,capital_view=capital_view)

# USER COMMISION DISPLAY
@auth.requires_login()
def usercommision():
    # Query Capital Money
    comm_qry =(db.LoanComm_Table.lc_user==auth.user.id)
    comm_view = db(comm_qry).select(db.LoanComm_Table.ALL,orderby=db.LoanComm_Table.lc_datepaid)
    # Total Capital calculation
    total_comm = 0
    for comx in comm_view:
        total_comm += comx.lc_amount
    
    return dict(auth=auth,total_comm=total_comm,comm_view=comm_view)

# ABOUT DEVELOPER PAGE
@auth.requires_login()
def aboutusp():

    return dict(auth=auth)


# WEBSITE PAGE
@auth.requires_login()
def websitep():

    return dict(auth=auth)


# TASK PAGE
@auth.requires_login()
def taskrep():
    # Query Capital Money
    loan_qry =(db.Loan_table.id>=1)
    loan_view = db(loan_qry).select(db.Loan_table.ALL,orderby=~db.Loan_table.id)

    return dict(auth=auth,loan_view=loan_view)


# LOAN DETAILS PAGE
@auth.requires_login()
def loandet():
    itm_id=''
    if request.vars:
        itm_id = request.vars.l_id   
        # Query Loan Information
        loan_qry =(db.Loan_table.id==int(itm_id))
        loan_view = db(loan_qry).select(db.Loan_table.ALL)

        # Query Loan Payments
        loanp_qry =(db.LoanPay_Table.lp_loan==int(itm_id))
        loanp_view = db(loanp_qry).select(db.LoanPay_Table.ALL)


    else:
        redirect(URL('reports', 'taskrep'))

    return dict(auth=auth,loan_view=loan_view,loanp_view=loanp_view)


# NOTICE PAGE
@auth.requires_login()
def noticerep():
    # Query Loan Payments
    not_qry =(db.Notice_Table.id>=1)
    not_view = db(not_qry).select(db.Notice_Table.ALL,orderby=~db.Notice_Table.id,limitby=((0,15)))
    return dict(auth=auth,not_view=not_view)


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
