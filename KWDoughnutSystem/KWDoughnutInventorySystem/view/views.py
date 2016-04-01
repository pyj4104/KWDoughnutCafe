import colander
import deform.widget
import math
import decimal
from datetime import datetime
from sqlalchemy import update, desc, asc
from sqlalchemy.sql import func
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from KWDoughnutInventorySystem.model.models import DBSession, Page, TransHistory, User, PriceScheme, Donation
import locale

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
                    DBSession.add(TransHistory(int(controls['scheme']), int(self.request.session["userID"]), controls['boxQuantity'], controls['doughnutQuantity'], defer))
                if ('donation' in controls and (controls['donation']!='' and float(controls['donation'])>0)):
                    donor = ''
                    if('donor' in controls):
                        donor = controls['donor']
                    DBSession.add(Donation(controls['donation'], donor))
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
                PriceScheme.doughnutPrice, TransHistory.deleted).join(User).join(PriceScheme).filter(TransHistory.deleted==0).order_by(desc(TransHistory.tid))
            return {'histories':history.all()}
        else:
            return HTTPFound(self.request.route_url('login'))

    @view_config(route_name='dhistory', renderer='./renderer/dhistory.pt')
    def donationHistory(self):
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            history = DBSession.query(Donation.tid, Donation.timeDonated, Donation.donor, Donation.amount).filter(Donation.deleted==0).order_by(desc(Donation.tid))
            return {'histories':history.all()}
        else:
            return HTTPFound(self.request.route_url('login'))

    @view_config(route_name='deleteDonation')
    def deleteDonation(self):
        controls = self.request.GET
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            DBSession.query(Donation).filter(Donation.tid==int(controls['tid'])).update({Donation.deleted:1})
        return HTTPFound(self.request.route_url('dhistory'))

    @view_config(route_name='statistics', renderer='./renderer/statistics.pt')
    def statistics(self): 
        locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            stats = DBSession.query(func.sum(TransHistory.boxesSold),
                func.sum(TransHistory.doughnutsSold),
                PriceScheme.boxPrice, PriceScheme.doughnutPrice).join(PriceScheme).filter(TransHistory.deleted==0).group_by(PriceScheme.tid).all()
            douhnutsSoldToday = DBSession.query(func.sum(TransHistory.boxesSold)).filter(TransHistory.deleted==0).filter(TransHistory.timeSold >= datetime.today().date()).scalar()
            donatedAmount = DBSession.query(func.sum(Donation.amount)).filter(Donation.deleted==0).scalar()
            initBoxes = 300
            boxSold = 0
            doughnutsSold = 0
            profit = 0
            inv = 1425
            moneyEarned = 0
            for scheme in stats:
                boxSold += scheme[0]
                doughnutsSold += scheme[1]
                moneyEarned += scheme[0] * decimal.Decimal(scheme[2]) + scheme[1] * decimal.Decimal(scheme[3])
            openedBoxes = math.ceil(doughnutsSold / 12)
            boxesLeft = initBoxes - boxSold - openedBoxes
            profit = float(moneyEarned-inv)
            return {'initBoxes':initBoxes, 'soldBoxes':boxSold, 'soldDoughnuts':doughnutsSold,
            'openBoxes':openedBoxes, 'boxesLeft':boxesLeft, 'monEarned':locale.currency(moneyEarned),
            'inv':locale.currency(inv), 'doughnutprofit':locale.currency(profit), 'soldToday':douhnutsSoldToday, 'donation':locale.currency(donatedAmount),
            'profit':locale.currency(profit+donatedAmount)}
        else:
            return HTTPFound(self.request.route_url('login'))

    @view_config(route_name='scheme', renderer='./renderer/pricescheme.pt')
    def price(self):
        session = self.request.session
        if ('userID' in session and session['userID']!=''):
            controls = self.request.POST
            if ('submit' in self.request.POST):
                try:
                    if (float(controls['boxPrice']) + float(controls['doughnutPrice']) >= 1):
                        DBSession.add(PriceScheme(controls['boxPrice'], controls['doughnutPrice']))
                    return {"msg":"Transaction Successful"}
                except:
                    return {"msg": "Transaction Unsuccessful. Please contact the server admin."}
            else:
                return {"msg":""}
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