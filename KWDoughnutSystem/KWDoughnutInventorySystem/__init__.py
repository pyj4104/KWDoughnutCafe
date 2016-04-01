from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .model.models import DBSession, Base
from pyramid.session import SignedCookieSessionFactory

def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config = Configurator(settings=settings,
                          root_factory='KWDoughnutInventorySystem.model.models.Root',
                          session_factory=my_session_factory)
    config.include('pyramid_chameleon')
    config.add_route('welcome', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('sellerpage', '/seller')
    config.add_route('transHistory', '/history')
    config.add_route('delete', '/delete')
    config.add_route('statistics', '/statistics')
    config.add_route('scheme', '/price')
    config.add_route('dhistory', '/dhistory')
    config.add_route('deleteDonation', '/deleteDonation')
    '''config.add_route('wikipage_add', '/add')
    config.add_route('wikipage_view', '/{uid}')
    config.add_route('wikipage_edit', '/{uid}/edit')'''
    config.add_static_view('deform_static', 'deform:static/')
    config.scan('.view.views')
    return config.make_wsgi_app()