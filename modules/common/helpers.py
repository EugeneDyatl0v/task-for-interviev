import random
import string
from typing import Any

from fastapi.templating import Jinja2Templates

import httpx

from jinja2 import Template

from logger import logger

from settings import UnisenderConfig


async def get_templates():
    templates = Jinja2Templates(
        directory='templates'
    )
    return templates


def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def remove_none_values(data: dict | list | Any) -> dict | list | Any:
    """
    Recursively removes properties with None values from all dictionaries in
    data including data itself

    Args:
        data (dict | list | Any): data to remove None properties from. If not
            dictionary or list, the function returns unchanged data

    Returns:
        initial dictionary without None properties
    """
    if isinstance(data, list):
        return [remove_none_values(item) for item in data if item is not None]
    elif isinstance(data, dict):
        return {
            key: remove_none_values(value) for key, value
            in data.items() if value is not None
        }
    else:
        return data


async def general_api_call(
        method_name: str,
        array_parameters: dict[str, str | dict] | None = None,
        query_parameters: dict[str, str] | None = None,
        **kwargs
) -> dict[str] | list[dict[str]]:
    """
    Wrapper for https.AsyncClient post method that passes parameters
    through form or query parameters

    Args:
        method_name (str): name of called Unisender API method. Examples:
            sendEmail, checkSms
        array_parameters (dict[str, str | dict]): parameters to be
            passed in array notation (e.g. fields[email]='user@auth0.com')
        query_parameters (dict[str, str]): parameters to be passed through
            url due to problems with passing them through form data
            (e.g. list_ids)
        kwargs (str | dict[str, str | dict[str, str]]): dictionary of
            other parameters to be passed with HTTP request

    Returns:
        data from 'result' property of JSON returned by Unisender API
        If API returns error response, raises exception
    """
    params = {}
    data = {
        'api_key': UnisenderConfig.api_key,
        'format': 'json'
    }
    kwargs = remove_none_values(kwargs)

    if array_parameters is not None:
        for parameter, fields in array_parameters.items():
            data.update({
                f'{parameter}[{key}]': value for key, value
                in fields.items()
            })

    if query_parameters is not None:
        params.update(query_parameters)

    data.update(kwargs)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'https://api.unisender.com/en/api/{method_name}',
            params=params,
            data=data
        )
        if response.is_error:
            logger.error(f'Error while sending email: {response.text}')
        if 'error' in response.json():
            logger.error(
                f'Error while sending email: {response.json().get('error')}'
            )
        return response.json().get('result')


async def get_template_body(
        template_id: str
) -> str:
    return (await general_api_call(
        method_name='getTemplate',
        template_id=template_id
    )).get('body')


def get_rendered_html(
        raw_html: str,
        params: dict[str, str]
):
    """Renders raw_html with replacement parameters and returns it"""
    template = Template(raw_html)
    return template.render(params)


async def send_email(
        subject: str,
        receiver_email: str,
        params: dict[str, str],
        template_id: str | None = None
) -> None:
    """
    Sends single email

    Args:
        subject (str): subject of email message
        receiver_email (str): email address of receiver
        params (dict[str, str]): parameters to be replaced in template
        template_id (str): id of template to be used in email body
    """
    raw_template_html = await get_template_body(template_id)
    body = get_rendered_html(
        raw_html=raw_template_html,
        params=params
    )
    await general_api_call(
        method_name='sendEmail',
        email=receiver_email,
        sender_name=UnisenderConfig.sender_name,
        sender_email=UnisenderConfig.sender_email,
        subject=subject,
        body=body,
        list_id=UnisenderConfig.default_list_id
    )
