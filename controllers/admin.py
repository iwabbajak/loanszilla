# ---- example index page ----
@auth.requires_login()
def index():
    return dict(auth=auth)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -- ADMIN DEVELOPER TABLES -- 
# USER TABLE
@auth.requires_login()
def crud_user():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.auth_user,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# USER GROUP TABLE
@auth.requires_login()
def crud_usergroup():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.auth_group,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# USER MEMBERSHIP
@auth.requires_login()
def crud_usergroupmember():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.auth_membership,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# USER MEMBERSHIPc 
@auth.requires_login()
def crud_ca():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.CapAdd_Table,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# BORROWER TABLE
@auth.requires_login()
def crud_borrow():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.Borrowers_table,user_signature=False,editable=False,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# BORROWER TABLE
@auth.requires_login()
def crud_term():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.Term_table,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# BORROWER TABLE
@auth.requires_login()
def crud_interest():
    export_classes = dict(csv=True, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    grid = SQLFORM.grid(db.Interest_table,user_signature=False,editable=True,deletable=False,exportclasses=export_classes)
    return dict(grid=grid)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TRANSACTIONAL PAGE
# ADD CAPITAL PAGE
@auth.requires_login()
def addcapital():
    user_select = ''
    ca_amount =''
    if request.vars:
        user_select = request.vars.user_select
        ca_amount = request.vars.ca_amount
        try:
            # Update Expense History
            db.CapAdd_Table.insert(
                ca_user=user_select,
                ca_amount=float(ca_amount),
                )
            db.commit()
            redirect(URL('default', 'index'))

        except:
            db.rollback()
            redirect(URL('default', 'action'))

    # Query Capital Money
    user_qry =(db.auth_user.id>=1)
    user_view = db(user_qry).select(db.auth_user.ALL,orderby=db.auth_user.first_name)
    return dict(user_view=user_view)


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
