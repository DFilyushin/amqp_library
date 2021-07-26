import logging
from copy import copy
from http.client import responses
from typing import Optional

import click


class ColoredFormatter(logging.Formatter):
    ACCESS = 25

    LEVEL_NAME_COLORS = {
        logging.NOTSET: 'cyan',
        logging.DEBUG: 'blue',
        logging.INFO: 'green',
        ACCESS: 'cyan',
        logging.WARNING: 'yellow',
        logging.ERROR: 'red',
        logging.CRITICAL: 'bright_red'
    }

    COLOR_STATUS_CODE = {
        '2': 'green',
        '3': 'yellow',
        '4': 'yellow',
        '5': 'red'
    }

    COLOR_STATUS = {
        'SUCCESS': 'green',
        'ERROR': 'red',
    }

    @staticmethod
    def _get_level_name_format(record) -> str:
        level_name_color = ColoredFormatter.LEVEL_NAME_COLORS[record.levelno]
        level_name_colored = click.style(record.levelname, fg=level_name_color)
        level_name_space = ' ' * (8 - len(record.levelname))
        return f'{level_name_colored}:{level_name_space}'

    @staticmethod
    def _get_method_format(record) -> str:
        method = record.args.get('method') \
            if 'method' in record.args and record.args.get('method') \
            else record.funcName
        return click.style(method, fg='blue')

    @staticmethod
    def _get_path_format(record) -> Optional[str]:
        path = record.args.get('path') if 'path' in record.args and record.args.get('path') else None
        return click.style(path, fg='blue') if path else None

    @staticmethod
    def _get_module_format(record) -> str:
        module = record.args.get('module') if 'module' in record.args and record.args.get('module') else None
        return click.style(module, fg='blue') if module else None

    @staticmethod
    def _get_file_format(record) -> str:
        path = f'{record.pathname}, line {record.levelno}'
        return click.style(path, fg='blue')

    @staticmethod
    def _get_common_message(record) -> str:
        method_format = ColoredFormatter._get_method_format(record)
        message = f'by the method: "{method_format}" and'

        if path_format := ColoredFormatter._get_path_format(record):
            message += f' path: "{path_format}".'
        elif module_format := ColoredFormatter._get_module_format(record):
            message += f' module: "{module_format}".'
        else:
            pathname_format = ColoredFormatter._get_file_format(record)
            message += f' file: "{pathname_format}".'

        if client_host := record.args.get('client_host'):
            client_host_colored = click.style(client_host, fg='blue')
            message += f' Client host: "{client_host_colored}".'

        if creator_id := record.args.get('creator_id'):
            creator_id_colored = click.style(creator_id, fg='blue')
            message += f' Creator id: "{creator_id_colored}".'

        return message

    @staticmethod
    def _get_access_message(record) -> str:
        common_message = ColoredFormatter._get_common_message(record)
        message = f'Access {common_message}'

        if status_code := record.args.get('status_code'):
            status_code_str = f'{status_code} {responses[status_code]}'
            status_code_color = ColoredFormatter.COLOR_STATUS_CODE[status_code_str[0]]
            status_code_colored = click.style(status_code_str, fg=status_code_color)
            message += f' Status code: "{status_code_colored}".'
        elif status := record.args.get('status'):
            status_color = ColoredFormatter.COLOR_STATUS[status]
            status_code_colored = click.style(status, fg=status_color)
            message += f' Status: "{status_code_colored}".'

        return message

    @staticmethod
    def _get_error_message(record) -> str:
        common_message = ColoredFormatter._get_common_message(record)
        message = f'Error {common_message}'

        request_param_collection = []

        if query_string := record.args.get('query_string'):
            request_param_collection.append(f'Query string: "{query_string}".')

        if form_params := record.args.get('form_params'):
            request_param_collection.append(f'Form params: "{form_params}".')

        if body := record.args.get('body'):
            request_param_collection.append(f'Body: "{body}".')

        if len(request_param_collection):
            request_param_str = ' '.join(request_param_collection)
            message += f' {request_param_str}'

        traceback = record.args.get('traceback')

        return f'{message} {traceback}'

    @staticmethod
    def _get_process_format(record) -> str:
        return click.style(str(record.process), fg='blue')

    def format(self, record) -> str:
        record_copy = copy(record)

        level_name_format = self._get_level_name_format(record_copy)
        time_format = self.formatTime(record, self.datefmt)

        if record.levelno == ColoredFormatter.ACCESS:
            message = self._get_access_message(record_copy)
        elif record.levelno == logging.ERROR:
            message = self._get_error_message(record_copy)
        else:
            message = record_copy.getMessage()

        process_format = self._get_process_format(record_copy)

        return f'{level_name_format} [{time_format}][{process_format}] - {message}'
