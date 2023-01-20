import os
import datetime
import time

# os.environ["TZ"] = "Asia/Manila"
# time.tzset()

#os.environ["TZ"] = "Asia/Singapore"
#time.tzset()
now = datetime.datetime.today()
# ------------------------------------

# ---- example index page ----
@auth.requires_login()
def index():
    return dict(auth=auth)


# ----------------------------------------------------------------------------------------------------------------------------------
# APPLY LOAN PAGE
@auth.requires_login()
def applyloan():
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

    #------ Total Money Paid from Loan  ------
    # Query Total Loan Payment Funds
    lp_qry =(db.LoanPay_Table.id>=1)
    lp_view = db(lp_qry).select(db.LoanPay_Table.ALL,orderby=db.LoanPay_Table.id)

    tloanp=0
    # Get Total Funds
    for x in lp_view:
        tloanp += x.lp_amount

    #------ Total Capital of User  ------ *New 20230105
    # Query Total Capital Funds
    cap_qry =(db.CapAdd_Table.ca_user==auth.user.id)
    cap_view = db(cap_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.id)

    total_cap = 0
    for cap_t in cap_view:
        total_cap += cap_t.ca_amount

     # Query Total Comaker Balance Funds
    borw_qry =(db.Loan_table.lt_comker==auth.user.id)&((db.Loan_table.lt_status=='RELEASE')|(db.Loan_table.lt_status=='SUCCEEDED'))
    borw_view = db(borw_qry).select(db.Loan_table.ALL,orderby=db.Loan_table.id)


    total_lbal = 0
    for bal_t in borw_view:
        total_lbal += bal_t.lt_balance


    total_allow = total_cap - total_lbal




    # l_amount, user_select2, l_reason
    user_select = ''
    l_amount =''
    l_reason = ''
    if request.vars:
        user_select = request.vars.user_select
        l_amount = request.vars.l_amount
        l_reason=  request.vars.l_reason

        try: 
            # Update Expense History
            db.Loan_table.insert(
                lt_amount = float(l_amount),
                lt_borrower = user_select,
                lt_reason = l_reason,
                lt_comker = auth.user.id,
                lt_amountapprove = float(l_amount),
                lt_interest = 1,
                lt_interestamount =(float(l_amount)*0.1),
                lt_term = 1,
                lt_balance = float(l_amount),
                lt_approveby = auth.user.id,
                lt_dateapproved =datetime.datetime.today(),
                lt_gcashreference='',
                lt_daterelease =datetime.datetime.today(),
                lt_releaseby= auth.user.id,
                lt_processingfee=0,
                lt_remarks='ONGOING',
                lt_status='INPROCESS',
                lt_additioninfo='',
                )
            db.commit()
            redirect(URL('default', 'index'))

        except:
            db.rollback()
            redirect(URL('default', 'action'))

    # Query Capital Money
    user_qry =(db.Borrowers_table.id>=1)
    user_view = db(user_qry).select(db.Borrowers_table.ALL,orderby=db.Borrowers_table.bt_firstname)
    return dict(user_view=user_view,tfunds=tfunds,tsubs=tsubs,tloanp=tloanp,
    total_cap=total_cap,total_lbal=total_lbal,total_allow=total_allow)


# LOAN PAYMENT PAGE
@auth.requires_login()
def loanpayment():
    itm_id=''
    if request.vars:
        itm_id = request.vars.l_id   
        # Query Loan Information
        loan_qry =(db.Loan_table.id==int(itm_id))
        loan_view = db(loan_qry).select(db.Loan_table.ALL)

    return dict(itm_id=itm_id,loan_view=loan_view)

# LOAN PAYMENT CONFIRM
@auth.requires_login()
def loanpayconf():
    l_id=''
    l_amount = 0
    gcash_ref = ''

    if request.vars:
        l_id = request.vars.l_id  
        l_amount = float(request.vars.l_amount)
        gcash_ref = request.vars.gcashref  

        # Make sure payment is not Zero
        if l_amount > 0:
            # Get Loan Info Via ID
            loan_qry =(db.Loan_table.id == int(l_id))
            loan_view = db(loan_qry).select().first()
            rembalance = loan_view.lt_balance - l_amount

            if rembalance <=0:
                 # Update loan record reflect payment
                loan_view.lt_balance = loan_view.lt_balance - l_amount
                loan_view.lt_status='FULLY PAID'
                loan_view.lt_remarks = 'PAID'
                loan_view.update_record() # saves above change
            else:
                 # Update loan record reflect payment
                loan_view.lt_balance = loan_view.lt_balance - l_amount
                loan_view.lt_status='SUCCEEDED'
                loan_view.update_record() # saves above change
           
            db.commit()

            # Insert Loan Payment Table
            try: 
                # Update Expense History
                db.LoanPay_Table.insert(
                    lp_loan = int(l_id),
                    lp_amount = float(l_amount),
                    lp_processby = auth.user.id,
                    lp_gcashreference = gcash_ref,
                    )
                db.commit()

                # INSERT NOTICE BOARD
                db.Notice_Table.insert(
                    nt_title = 'LOAN PAYMENT',
                    nt_message = 'PAID by ' + loan_view.lt_borrower.bt_firstname + " " +loan_view.lt_borrower.bt_lastname,
                )
                db.commit()

                redirect(URL('default', 'home'))

            except:
                db.rollback()
                redirect(URL('apploan', 'loanlist'))
            
            
            # Get Loan Info Via ID
            loan_qry =(db.Loan_table.id == int(l_id))
            loan_view2 = db(loan_qry).select(db.Loan_table.ALL)

            # Get all Loan Payment
            loanpay_qry =(db.LoanPay_Table.lp_loan == int(l_id))
            loanpay_view = db(loanpay_qry).select(db.LoanPay_Table.ALL)

            
    return dict(loanpay_view=loanpay_view,loan_view2=loan_view2)

# ----------------------------------------------------------------------------------------------------------------------------------
# APPROVED LOAN PAGE
@auth.requires_login()
def appproveloan():
  
 
    itm_id=''
    if request.vars:
        itm_id = request.vars.l_id   
        # Query Loan Information
        loan_qry =(db.Loan_table.id==int(itm_id))
        loan_view = db(loan_qry).select(db.Loan_table.ALL)

    # Query Capital Money
    user_qry =(db.Borrowers_table.id>=1)
    user_view = db(user_qry).select(db.Borrowers_table.ALL,orderby=db.Borrowers_table.bt_firstname)

    # Query Interest
    int_qry =(db.Interest_table.id>=1)
    int_view = db(int_qry).select(db.Interest_table.ALL,orderby=db.Interest_table.id)
    
    # Query Term
    trm_qry =(db.Term_table.id>=1)
    trm_view = db(trm_qry).select(db.Term_table.ALL,orderby=db.Term_table.id)
      
    return dict(loan_view=loan_view,trm_view=trm_view,int_view=int_view)

# APPROVE LOAN CONFIRM
@auth.requires_login()
def approveconf():
    l_id=''
    l_amount = 0
    int_select = 0
    trm_select = 0
    rjc_select = ''
    if request.vars:
        l_id = request.vars.l_id  
        l_amount = float(request.vars.l_amount)
        int_select =  float(request.vars.int_select)
        trm_select =  request.vars.trm_select
        rjc_select = request.vars.rjc_select  
     
        # Get Loan Info Via ID
        loan_qry =(db.Loan_table.id == int(l_id))
        loan_view = db(loan_qry).select().first()

        # Get Interest Info
        int_qry =(db.Interest_table.id == int(int_select))
        int_view = db(int_qry).select().first()

        if rjc_select == 'No':
            # Update Loan Info
            loan_view.lt_amount= l_amount
            loan_view.lt_amountapprove= l_amount
            loan_view.lt_interest= int_select
            loan_view.lt_term= trm_select
            loan_view.lt_balance= l_amount
            loan_view.lt_interestamount= l_amount * int_view.it_interest
            loan_view.lt_approveby= auth.user.id
            loan_view.lt_dateapproved = datetime.datetime.today()
            loan_view.lt_status='APPROVED'
            loan_view.update_record() # saves above change
        elif rjc_select == 'Yes':
             # Update Loan Info
            loan_view.lt_amountapprove= l_amount
            loan_view.lt_interest= int_select
            loan_view.lt_term= trm_select
            loan_view.lt_dateapproved = datetime.datetime.today()
            loan_view.lt_status='REJECTED'
            loan_view.update_record() # saves above change


        # Get Loan Info Via ID
        loan_qry =(db.Loan_table.id == int(l_id))
        loan_view2 = db(loan_qry).select(db.Loan_table.ALL)



    return dict(l_amount=l_amount,int_select=int_select,trm_select=trm_select,rjc_select=rjc_select,loan_view2=loan_view2)

# ----------------------------------------------------------------------------------------------------------------------------------
# RELEASE LOAN PAGE
@auth.requires_login()
def releaseloan():
    itm_id=''
    if request.vars:
        itm_id = request.vars.l_id   
        # Query Loan Information
        loan_qry =(db.Loan_table.id==int(itm_id))
        loan_view = db(loan_qry).select(db.Loan_table.ALL)
    return dict(loan_view=loan_view)

# RELEASE LOAN CONFIRM
@auth.requires_login()
def releaseconf():
    l_id=''
    gcash_ref = ''

    # Query Capital Money
    capital_qry =(db.CapAdd_Table.id>=1)
    capital_view = db(capital_qry).select(db.CapAdd_Table.ALL,orderby=db.CapAdd_Table.ca_datetime)
    # Total Capital calculation
    total_capital = 0
    for capx in capital_view:
        total_capital += capx.ca_amount

   
    
    if request.vars:
        l_id = request.vars.l_id  
        gcash_ref = request.vars.gcashref  

        # Get Loan Info Via ID
        loan_qry =(db.Loan_table.id == int(l_id))
        loan_view = db(loan_qry).select().first()

        # Update Loan Info
        loan_view.lt_gcashreference= gcash_ref
        loan_view.lt_daterelease= datetime.datetime.today()
        loan_view.lt_releaseby= auth.user.id
        loan_view.lt_amountrelease = loan_view.lt_amount - loan_view.lt_interestamount
        loan_view.lt_status='RELEASE'
        loan_view.update_record() # saves above change

        try: 
            # Update Expense History
            db.CapSub_Table.insert(
                cs_user = auth.user.id,
                cs_amount = loan_view.lt_amount - loan_view.lt_interestamount,
                cs_reaseon = 'Loan Releasing',
                cs_datetime = datetime.datetime.today(),
                cs_refloan = loan_view.id
                )
            db.commit()
            # UPDATE COMAKER AND ADMIN FEES
            # Get Comaker Percentage added to Comaker Commision [20%]
            db.LoanComm_Table.insert(
                lc_loan = loan_view.id,
                lc_amount = loan_view.lt_interestamount * 0.2,
                lc_user = loan_view.lt_comker,
                lc_percentage = 0.2,
                lc_processby = auth.user.id,
                lc_comtype = 'CC',
                )
            db.commit()
             # Get Admin Percentage added to Admin Commision [20%] User always User id1 the Developer
            db.LoanComm_Table.insert(
                lc_loan = loan_view.id,
                lc_amount = loan_view.lt_interestamount * 0.2,
                lc_user = 1,
                lc_percentage = 0.2,
                lc_processby = auth.user.id,
                lc_comtype = 'AC',
                )
            db.commit()



            # UPDATE ALL USER [60%] SHARING
            for x in capital_view:
                db.LoanComm_Table.insert(
                lc_loan = loan_view.id,
                lc_amount = round((loan_view.lt_interestamount * 0.6) * (x.ca_amount/total_capital),2),
                lc_user = x.ca_user.id,
                lc_percentage = 0.6,
                lc_processby = auth.user.id,
                lc_comtype = 'LC',
                )
            db.commit()

            # INSERT NOTICE BOARD
            db.Notice_Table.insert(
                nt_title = 'LOAN RELEASED',
                nt_message = 'Release to '  + loan_view.lt_borrower.bt_firstname + " " +loan_view.lt_borrower.bt_lastname,
            )
            db.commit()

            redirect(URL('default', 'index'))

        except:
            db.rollback()
            redirect(URL('default', 'action'))       

         # Get Loan Info Via ID
        loan_qry =(db.Loan_table.id == int(l_id))
        loan_view2 = db(loan_qry).select(db.Loan_table.ALL)


    return dict(loan_view2=loan_view2)






# ----------------------------------------------------------------------------------------------------------------------------------
# LOAN LIST PAGE
@auth.requires_login()
def loanlist():
     # Query Capital Money
    loan_qry =(db.Loan_table.id>=1)&(db.Loan_table.lt_status!='REJECTED')&(db.Loan_table.lt_status!='FULLY PAID')
    loan_view = db(loan_qry).select(db.Loan_table.ALL,orderby=~db.Loan_table.id)
    deltadays_arr = []
    for x in loan_view:
       delta_dys = now - datetime.datetime.strptime(x.lt_daterelease, '%Y-%m-%d %H:%M:%S.%f')  
       deltadays_arr.append(delta_dys)

    ugroup = auth.user_groups.values()
    return dict(loan_view=loan_view,deltadays_arr=deltadays_arr,ugroup=ugroup)




















# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
