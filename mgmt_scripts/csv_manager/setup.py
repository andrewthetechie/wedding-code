from setuptools import setup

setup(
    name="wedding-manager-csv-manager",
    version="0.1",
    py_modules=["csv_manager"],
    install_requires=[
        'Click',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        wm-csv-man=csv_manager:cli
    '''
)
