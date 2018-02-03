import csv
import json
from datetime import datetime

import click
import requests
from tqdm import tqdm


def _add_guest(
        wedding_manager_url: str,
        wedding_manager_username: str,
        wedding_manager_pass: str,
        name: str,
        phone_number: str,
        email_address: str,
        physical_address: str,
        total_attendees: int):
    """
    Adds a guest to the wedding manager via api call
    Args:
        wedding_manager_url (str): URL of wedding manager
        wedding_manager_username (str): username for wedding manager
        wedding_manager_pass (str): password for wedding manager
        name (str): Name of guest
        phone_number (str): Phone number of guest
        email_address (str): Email address of guest
        physical_address (str): Physical address of guest
        total_attendees (int): Total number of guests

    Returns:
        Bool
    """

    data = {
        'name': name,
        'total_attendees': total_attendees,
        'phone_number': phone_number,
        'email_address': email_address,
        'physical_address': physical_address
    }
    # ToDo: Handle auth
    guest_url = "{}/guest".format(wedding_manager_url)
    response = requests.post(url=guest_url, json=data)

    return True if response.status_code == 201 else False


def _get_guest_list_from_file(csv_file: click.File,
                              lines_to_skip: int):
    """
    Turns a file handler of a CSV file into a python list object
    Args:
        csv_file (click.File): File handler
        lines_to_skip (int): Number of lines to skip

    Returns:
        list
    """
    csv_reader = csv.reader(csv_file)
    return list(csv_reader)[lines_to_skip:]


def _get_guest_list_from_wm(wedding_manager_url: str,
                            wedding_manager_username: str,
                            wedding_manager_pass: str,):
    """
    Retries a list of all guests from wedding manager
    Args:
        wedding_manager_url (str): URL of wedding manager
        wedding_manager_username (str): username for wedding manager
        wedding_manager_pass (str): password for wedding manager

    Returns:
        list or bool
    """
    guests_url = "{}/guests".format(wedding_manager_url)
    response = requests.get(url=guests_url)
    return response.json() if response.status_code == 200 else False


@click.group()
@click.option('--wm_api_url', default="http://wm-api:5000/api", envvar="WM_API_URL")
@click.option('--wm_api_user', default="admin", envvar="WM_API_USER")
@click.option('--wm_api_pass', default="pass", envvar="WM_API_PASS")
@click.pass_context
def cli(ctx,
        wm_api_url: str,
        wm_api_user: str,
        wm_api_pass: str):
    ctx.obj = dict()
    ctx.obj['WM_API_URL'] = wm_api_url
    ctx.obj['WM_API_USER'] = wm_api_user
    ctx.obj['WM_API_PASS'] = wm_api_pass
    pass


@cli.command(name="import")
@click.option('--skip_lines', default=0, type=int, help="Lines to skip from the top of the csv")
@click.argument('csv_file', type=click.File('r'))
@click.pass_context
def _import(ctx,
            csv_file: click.File,
            skip_lines: int):
    """
    Import imports a CSV file into our wedding manager

    """
    # get our guest list
    guest_list = _get_guest_list_from_file(csv_file, skip_lines)

    click.echo("About to import {guests} guests from {filename}".format(guests=len(guest_list),
                                                                        filename=csv_file.name))
    click.confirm('Do you want to continue?', abort=True)

    for guest in tqdm(guest_list):
        if _add_guest(ctx.obj['WM_API_URL'],
                      ctx.obj['WM_API_USER'],
                      ctx.obj['WM_API_PASS'],
                      guest[0],
                      guest[1],
                      guest[2],
                      guest[3],
                      int(guest[4])):
            tqdm.write("Added {}".format(guest))
        else:
            tqdm.write("Failed to add {}".format(guest))


@cli.command()
@click.option('--no_header', default=False, type=bool, is_flag=True)
@click.argument('csv_file_name', type=str,
                default="./wm-out-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H-%M")))
@click.pass_context
def export(ctx,
           csv_file_name: str,
           no_header: bool):
    """
    Exports our wedding manager guestbook to a CSV file

    Args:
        ctx: Context from cli
        csv_file_name (str): Path to a Writeable file that we're going to write to
        no_header (bool): If

    """
    guest_list = _get_guest_list_from_wm(ctx.obj['WM_API_URL'],
                                         ctx.obj['WM_API_USER'],
                                         ctx.obj['WM_API_PASS'])

    click.echo("About to write info about {guests} guests to {filename}".format(guests=len(guest_list),
                                                                                filename=csv_file_name))
    click.confirm('Do you want to continue?', abort=True)

    keys = guest_list[0].keys()
    with open(csv_file_name, 'w') as file_handler:
        writer = csv.DictWriter(file_handler, keys)
        if not no_header:
            writer.writeheader()
        writer.writerows(guest_list)

    click.echo("Dumped Wedding Manager Guest list to {}".format(csv_file_name))
