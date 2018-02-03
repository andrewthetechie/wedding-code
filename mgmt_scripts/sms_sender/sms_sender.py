import click
import requests
from tqdm import tqdm
from twilio.rest import Client
from jinja2 import Environment


def _get_all_contact_users(url: str,
                           username: str,
                           password: str):
    """
    Returns a list of users (as dicts) that have not opted out of SMS contact
    Args:
        url (str): Url of the WM instance
        username (str): Username for the WM instance
        password (str): Password for the WM Instance

    Returns:
        list[dict]
    """
    response = requests.get(url="{}/guests?guest_filter=all_contacts".format(url))
    return response.json()


def _get_rsvp_users(url: str,
                    username: str,
                    password: str):
    """
    Returns a list of users (as dicts) that want an RSVP notice from us
    Args:
        url (str): Url of the WM instance
        username (str): Username for the WM instance
        password (str): Password for the WM Instance

    Returns:
        list[dict]
    """
    first_query = requests.get("{}/guests?guest_filter=savethedate&guest_value=None".format(url))
    second_query = requests.get("{}/guests?guest_filter=savethedate&guest_value=True".format(url))
    return first_query.json() + second_query.json()


def _get_not_yet_rsvp_users(url: str,
                    username: str,
                    password: str):
    """
    Returns a list of users (as dicts) that have not yet RSVPD
    Args:
        url (str): Url of the WM instance
        username (str): Username for the WM instance
        password (str): Password for the WM Instance

    Returns:
        list[dict]
    """
    first_query = requests.get("{}/guests?guest_filter=savethedate&guest_value=False".format(url))
    second_query = requests.get("{}/guests?guest_filter=rsvp&guest_value=None".format(url))
    return [user for user in second_query.json() if user not in first_query.json()]


def _render_template(template: str, user: dict):
    """
    Renders a jinja template (template) using a dict (user)

    Args:
        template (str): String Jinja template
        user (dict): Dictionary of a user

    Returns:
        str
    """
    return Environment().from_string(template).render(**user)


def _send_messages(ctx, user_list: list, template: str):
    """
    Loops through our user list and sends them message, if not in test mode
    Args:
        ctx: CLick context object
        user_list (list): List of users to send to
        template (str): Message to send
    """
    if not ctx.obj['TEST_MODE']:
        click.echo("About to send SMS template to {} users".format(len(user_list)))
        click.echo("Template:\n {}".format(template))
        click.confirm('Do you want to continue?', abort=True)
        for user in tqdm(user_list):
            message = _render_template(template, user)
            _send_message(ctx.obj['TW_CLIENT'], user['phone_number'], ctx.obj['TW_FROM_NUMBER'], message)
            tqdm.write("Sent template to {name} at {number}".format(name=user['name'], number=user['phone_number']))
    else:
        click.echo("We would send messages to {} users".format(len(user_list)))
        click.echo("Template:\n {}".format(template))
        click.echo("User List:\n {}".format(user_list))
        click.echo("Rendered template with first user: {}".format(_render_template(template, user_list[0])))


def _send_message(client,
                  to_num: str,
                  from_num: str,
                  message: str,
                  ):
    """
    Sends a message via twilio
    Args:
        client (twilio.rest.Client): Client to send the message with
        to_num (str): Number to send to
        from_num (str): Number to send from
        message (str): Message to send

    """
    client.api.account.messages.create(to=to_num,
                                      from_=from_num,
                                      body=message)


@click.group()
@click.option('--wm_api_url', default="http://wm-api:5000/api", envvar="WM_API_URL")
@click.option('--wm_api_user', default="admin", envvar="WM_API_USER")
@click.option('--wm_api_pass', default="pass", envvar="WM_API_PASS")
@click.option('--account_sid', envvar="TW_ACCNT_SID")
@click.option('--auth_token',  envvar="TW_AUTH_TOKEN")
@click.option('--from_number',  envvar="TW_FROM_NUMBER")
@click.option('--test', help="Test, dont actually send the SMS", is_flag=True, default=False)
@click.pass_context
def cli(ctx,
        wm_api_url: str,
        wm_api_user: str,
        wm_api_pass: str,
        account_sid: str,
        auth_token: str,
        from_number: str,
        test: bool):
    ctx.obj = dict()
    ctx.obj['WM_API_URL'] = wm_api_url
    ctx.obj['WM_API_USER'] = wm_api_user
    ctx.obj['WM_API_PASS'] = wm_api_pass
    ctx.obj['TW_CLIENT'] = Client(account_sid, auth_token)
    ctx.obj['TW_FROM_NUMBER'] = from_number
    ctx.obj['TEST_MODE'] = test
    pass


@cli.command()
@click.argument('template_file', type=click.File('r'))
@click.pass_context
def save_the_date(ctx,
                  template_file: click.File):
    user_list = _get_all_contact_users(ctx.obj['WM_API_URL'], ctx.obj['WM_API_USER'], ctx.obj['WM_API_PASS'])
    message = template_file.read()
    _send_messages(ctx, user_list, message)


@cli.command()
@click.argument('template_file', type=click.File('r'))
@click.pass_context
def rsvp(ctx,
         template_file: click.File):
    user_list = _get_rsvp_users(ctx.obj['WM_API_URL'], ctx.obj['WM_API_USER'], ctx.obj['WM_API_PASS'])
    message = template_file.read()
    _send_messages(ctx, user_list, message)


@cli.command()
@click.argument('template_file', type=click.File('r'))
@click.pass_context
def rsvp_chase(ctx,
               template_file: click.File):
    user_list = _get_not_yet_rsvp_users(ctx.obj['WM_API_URL'], ctx.obj['WM_API_USER'], ctx.obj['WM_API_PASS'])
    message = template_file.read()
    _send_messages(ctx, user_list, message)


@cli.command()
@click.argument('template_file', type=click.File('r'))
@click.pass_context
def update(ctx,
           template_file: click.File):
    user_list = _get_all_contact_users(ctx.obj['WM_API_URL'], ctx.obj['WM_API_USER'], ctx.obj['WM_API_PASS'])
    message = template_file.read()
    _send_messages(ctx, user_list, message)