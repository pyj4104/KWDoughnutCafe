from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .model.models import DBSession, Base

def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          root_factory='KWDoughnutInventorySystem.model.models.Root')
    config.include('pyramid_chameleon')
    config.add_route('welcome', '/')
    config.add_route('login', '/login')
    config.add_route('sellerpage', '/seller')
    config.add_route('submitOrder', '/submitOrder')
    '''config.add_route('wikipage_add', '/add')
    config.add_route('wikipage_view', '/{uid}')
    config.add_route('wikipage_edit', '/{uid}/edit')'''
    config.add_static_view('deform_static', 'deform:static/')
    config.scan('.view.views')
    return config.make_wsgi_app()