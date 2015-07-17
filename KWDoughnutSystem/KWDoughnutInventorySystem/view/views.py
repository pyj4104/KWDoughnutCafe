import colander
import deform.widget
import math
import decimal
from sqlalchemy import update
from sqlalchemy.sql import func
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from KWDoughnutInventorySystem.model.models import DBSession, Page, TransHistory, User, PriceScheme

class WikiPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )

class WikiViews(object):
    def __init__(self, request):
        self.request = request

    @property
    def wiki_form(self):
        schema = WikiPage()
        return deform.Form(schema, buttons=('submit',))

    @property
    def reqts(self):
        return self.wiki_form.get_widget_resources()

    @view_config(route_name='welcome', renderer='./renderer/welcome.pt')
    def welcome(self):
        return {'':''}

    @view_config(route_name='login', renderer='./renderer/login.pt')
    def login(self):
        session = self.request.session
        if('userID' not in session or session['userID']==''):
            controls = self.request.POST
            if('form.submitted' in self.request.POST):
                info = DBSession.query(User.uid).filter(User.name==controls['login'],
                                     User.password==controls['password'])
                if (DBSession.query(info.exists())):
                    session["userID"] = info.scalar()
                    return HTTPFound(self.request.route_url('sellerpage'))
                else:
                    return HTTPFound(self.request.route_url('welcome'))
            else:
                return {"message":"Please Log In"}
        else:
            return HTTPFound(self.request.route_url('sellerpage'))

    @view_config(route_name='logout')
    def logout(self):
        session = self.request.session
        session["userID"] = ''
        return HTTPFound(self.request.route_url('welcome'))

    @view_config(route_name='delete')
    def delete(self):
        controls = self.request.GET
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            DBSession.query(TransHistory).filter(TransHistory.tid==int(controls['tid'])).update({TransHistory.deleted:1,
                TransHistory.deletedUsrInit:(DBSession.query(User.name).filter(User.uid==session['userID']).scalar())})
        return HTTPFound(self.request.route_url('transHistory'))

    @view_config(route_name='sellerpage', renderer='./renderer/sellerpage.pt')
    def seller(self):
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            controls = self.request.POST
            if ('submit' in self.request.POST):
                if ('defer' in controls):
                    defer = controls['defer']
                else:
                    defer = False
                if (int(controls['boxQuantity']) + int(controls['doughnutQuantity']) >= 1):
                    DBSession.add(TransHistory(1, int(self.request.session["userID"]), controls['boxQuantity'], controls['doughnutQuantity'], defer))
                return {"msg":"Transaction Successful"}
            else:
                return {"msg":""}
        else:
            return HTTPFound(self.request.route_url('login'))

    @view_config(route_name='transHistory', renderer='./renderer/history.pt')
    def transHistory(self):
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            history = DBSession.query(TransHistory.tid, TransHistory.timeSold, User.name, TransHistory.boxesSold,
                TransHistory.doughnutsSold, TransHistory.deferredPayment, PriceScheme.boxPrice,
                PriceScheme.doughnutPrice, TransHistory.deleted).join(User).join(PriceScheme).filter(TransHistory.deleted==0)
            return {'histories':history.all()}
        else:
            return HTTPFound(self.request.route_url('login'))

    @view_config(route_name='statistics', renderer='./renderer/statistics.pt')
    def statistics(self):
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            stats1 = DBSession.query(func.sum(TransHistory.boxesSold),
                func.sum(TransHistory.doughnutsSold),
                PriceScheme.boxPrice, PriceScheme.doughnutPrice).join(PriceScheme).filter(TransHistory.deleted==0)
            hi = stats1.first()
            boxSold = hi[0]
            doughnutsSold = hi[1]
            openedBoxes = math.ceil(doughnutsSold / 12)
            boxesLeft = 300 - boxSold - openedBoxes
            moneyEarned = boxSold * decimal.Decimal(hi[2]) + doughnutsSold * decimal.Decimal(hi[3])
            profit = 0
            inv = 0
            return {'initBoxes':300, 'soldBoxes':boxSold, 'soldDoughnuts':doughnutsSold,
            'openBoxes':openedBoxes, 'boxesLeft':boxesLeft, 'monEarned':moneyEarned,
            'inv':0, 'profit':0}
        else:
            return HTTPFound(self.request.route_url('login'))

    """@view_config(route_name='wiki_view', renderer='wiki_view.pt')
    def wiki_view(self):
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Wiki View', pages=pages)

    @view_config(route_name='wikipage_add',
                 renderer='wikipage_addedit.pt')
    def wikipage_add(self):
        form = self.wiki_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            # Add a new page to the database
            new_title = appstruct['title']
            new_body = appstruct['body']
            DBSession.add(Page(title=new_title, body=new_body))

            # Get the new ID and redirect
            page = DBSession.query(Page).filter_by(title=new_title).one()
            new_uid = page.uid

            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)


    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(uid=uid).one()
        return dict(page=page)


    @view_config(route_name='wikipage_edit',
                 renderer='wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(uid=uid).one()

        wiki_form = self.wiki_form

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=page, form=e.render())

            # Change the content and redirect to the view
            page.title = appstruct['title']
            page.body = appstruct['body']
            url = self.request.route_url('wikipage_view', uid=uid)
            return HTTPFound(url)

        form = self.wiki_form.render(dict(
            uid=page.uid, title=page.title, body=page.body)
        )

        return dict(page=page, form=form)"""