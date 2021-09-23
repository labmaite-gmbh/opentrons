""" update-server implementation for openembedded systems """
import asyncio
import logging
from aiohttp import web

# , name_management

from . import config, constants, control, ssh_key_management, update
from openembedded import root_fs

LOG = logging.getLogger(__name__)


@web.middleware
async def log_error_middleware(request, handler):
    try:
        resp = await handler(request)
    except Exception:
        LOG.exception(f"Exception serving {request.method} {request.path}")
        raise
    return resp


def get_app(system_version_file: str = None,
            config_file_override: str = None,
            name_override: str = None,
            boot_id_override: str = None,
            rfs: root_fs.RootFS = root_fs.RootFS(),
            loop: asyncio.AbstractEventLoop = None) -> web.Application:
    """ Build and return the aiohttp.web.Application that runs the server

    """

    LOG.info('TODO')

    if not loop:
        loop = asyncio.get_event_loop()

    name = 'todo'
    boot_id = 'todo'

    config_obj = config.load(config_file_override)

    app = web.Application(middlewares=[log_error_middleware])
    app[config.CONFIG_VARNAME] = config_obj
    app[constants.RESTART_LOCK_NAME] = asyncio.Lock()
    app[constants.DEVICE_BOOT_ID_NAME] = boot_id
    app[constants.DEVICE_NAME_VARNAME] = name
    app.router.add_routes([
        web.post('/server/update/begin', update.begin),
        web.post('/server/update/cancel', update.cancel),
        web.get('/server/update/{session}/status', update.status),
        web.post('/server/update/{session}/file', update.file_upload),
        web.post('/server/update/{session}/commit', update.commit),
        web.post('/server/restart', control.restart),
        web.get('/server/ssh_keys', ssh_key_management.list_keys),
        web.post('/server/ssh_keys', ssh_key_management.add),
        web.delete('/server/ssh_keys', ssh_key_management.clear),
        web.delete('/server/ssh_keys/{key_md5}', ssh_key_management.remove),
        # web.post('/server/name', name_management.set_name_endpoint),
        # web.get('/server/name', name_management.get_name_endpoint),
    ])
    return app