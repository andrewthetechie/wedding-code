from setuptools import setup

setup(
    name="wedding-manager-sms-sender",
    version="0.1",
    py_modules=["sms_sender"],
    install_requires=[
        'Click',
        'requests',
        'twilio',
        'tqdm',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        wm-sms-send=sms_sender:cli
    '''
)
