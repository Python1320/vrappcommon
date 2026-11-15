import os

from vrappcommon.jankyguihelpers import fatal
from vrappcommon.task_helper import spawn_task
import asyncio
import openvr
import openvr.error_code
import logging

vr_system_fut: asyncio.Future[openvr.IVRSystem] | None = None
vr_system_task: asyncio.Task[None] | None = None

vr_system_first = True


async def _get_vr_system(app_type=openvr.VRApplication_Overlay, identity=''):
	if not vr_system_fut:
		raise RuntimeError('Future not initialized')

	if vr_system_fut.done():
		raise RuntimeError('VR System already initialized')

	if not identity:
		identity = IDENTITY

	init_errored = False
	for i in range(999999):
		try:
			vr_system = openvr.init(app_type)
			if not vr_system_fut.done():
				vr_system_fut.set_result(vr_system)
			if identity:
				try:
					openvr.VRApplications().identifyApplication(os.getpid(), identity)
				except openvr.error_code.ApplicationError_UnknownApplication:
					logging.exception('cannot register')
			logging.info('OpenVR initialized successfully')
			break
		except asyncio.CancelledError:
			if not vr_system_fut.done():
				vr_system_fut.cancel()
			raise
		except openvr.error_code.InitError_Init_VRClientDLLNotFound as e:
			if not vr_system_fut.done():
				vr_system_fut.set_exception(e)
			raise
		except openvr.error_code.InitError_Init_HmdNotFound:
			if not init_errored:
				init_errored = True
				print('Waiting for headset (HDM)...')
		except openvr.error_code.InitError_Init_HmdNotFoundPresenceFailed:
			if not init_errored:
				init_errored = True
				print('Waiting for headset (HDM)...')
		except openvr.error_code.InitError_Init_NoServerForBackgroundApp:
			if not init_errored:
				init_errored = True
				print('Waiting for SteamVR...')
		except Exception as e:
			if not vr_system_fut.done():
				vr_system_fut.set_exception(e)
			fatal(f'Failed to initialize OpenVR: {e}')
			raise
		await asyncio.sleep(2.1)


async def get_vr_system(
	app_type=openvr.VRApplication_Overlay,
	loop: asyncio.AbstractEventLoop | None = None,
	identity='',
	task_group: asyncio.TaskGroup | None = None,
) -> openvr.IVRSystem:
	global vr_system_first, vr_system_fut, vr_system_task
	if vr_system_first:
		vr_system_first = False
		loop = loop or asyncio.get_running_loop()
		assert loop is not None, 'Loop must be provided on first call'
		vr_system_fut = asyncio.Future(loop=loop)
		vr_system_task = spawn_task(
			_get_vr_system(app_type, identity),
			loop=task_group or loop,
			name='get_vr_system',
		)
	assert vr_system_fut
	await vr_system_fut
	return vr_system_fut.result()


identity = ''


def set_identity(identity: str):

	if vr_system_fut and vr_system_fut.done():
		raise RuntimeError('VR System already initialized')
	global IDENTITY
	IDENTITY = identity
