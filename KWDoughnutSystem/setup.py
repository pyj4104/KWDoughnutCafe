from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform',
    'sqlalchemy',
    'pyramid_tm',
    'zope.sqlalchemy'
]

setup(name='KWDoughnutInventorySystem',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = KWDoughnutInventorySystem:main
      [console_scripts]
      initialize_tutorial_db = KWDoughnutInventorySystem.initialize_db:main
      """,
      packages=['model', 'view'],
      package_dir={'model': 'KWDoughnutInventorySystem/model', 'view': 'KWDoughnutInventorySystem/view'},
)