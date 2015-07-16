from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform',
    'sqlalchemy',
    'pyramid_tm',
    'zope.sqlalchemy'
]

setup(name='DoughnutSystem',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = DoughnutSystem:main
      [console_scripts]
      initialize_tutorial_db = DoughnutSystem.initialize_db:main
      """,
)