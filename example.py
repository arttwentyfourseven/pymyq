"""Run an example script to quickly test."""
import asyncio
import logging

from aiohttp import ClientSession

from pymyq import login
from pymyq.account import MyQAccount
from pymyq.errors import MyQError, RequestError
from pymyq.garagedoor import STATE_CLOSED, STATE_OPEN

_LOGGER = logging.getLogger()

EMAIL = "<EMAIL>"
PASSWORD = "<PASSWORD>"
ISSUE_COMMANDS = False


def print_info(number: int, device):
    """Print the device information

    Args:
        number (int): [description]
        device ([type]): [description]
    """
    print(f"      Device {number + 1}: {device.name}")
    print(f"      Device Online: {device.online}")
    print(f"      Device ID: {device.device_id}")
    print(
        f"      Parent Device ID: {device.parent_device_id}",
    )
    print(f"      Device Family: {device.device_family}")
    print(
        f"      Device Platform: {device.device_platform}",
    )
    print(f"      Device Type: {device.device_type}")
    print(f"      Firmware Version: {device.firmware_version}")
    print(f"      Open Allowed: {device.open_allowed}")
    print(f"      Close Allowed: {device.close_allowed}")
    print(f"      Current State: {device.state}")
    print("      ---------")


async def print_garagedoors(account: MyQAccount):
    """Print garage door information and open/close if requested

    Args:
        account (MyQAccount): Account for which to retrieve garage doors
    """
    print(f"  GarageDoors: {len(account.covers)}")
    print("  ---------------")
    if len(account.covers) != 0:
        for idx, device in enumerate(account.covers.values()):
            print_info(number=idx, device=device)

            if ISSUE_COMMANDS:
                try:
                    if device.open_allowed:
                        if device.state == STATE_OPEN:
                            print(f"Garage door {device.name} is already open")
                        else:
                            print(f"Opening garage door {device.name}")
                            try:
                                if await device.open(wait_for_state=True):
                                    print(f"Garage door {device.name} has been opened.")
                                else:
                                    print(f"Failed to open garage door {device.name}.")
                            except MyQError as err:
                                _LOGGER.error(
                                    "Error when trying to open %s: %s",
                                    device.name,
                                    str(err),
                                )
                    else:
                        print(f"Opening of garage door {device.name} is not allowed.")

                    if device.close_allowed:
                        if device.state == STATE_CLOSED:
                            print(f"Garage door {device.name} is already closed")
                        else:
                            print(f"Closing garage door {device.name}")
                            wait_task = None
                            try:
                                wait_task = await device.close(wait_for_state=False)
                            except MyQError as err:
                                _LOGGER.error(
                                    "Error when trying to close %s: %s",
                                    device.name,
                                    str(err),
                                )

                            print(f"Device {device.name} is {device.state}")

                            if (
                                wait_task
                                and isinstance(wait_task, asyncio.Task)
                                and await wait_task
                            ):
                                print(f"Garage door {device.name} has been closed.")
                            else:
                                print(f"Failed to close garage door {device.name}.")

                except RequestError as err:
                    _LOGGER.error(err)
        print("  ------------------------------")


async def print_lamps(account: MyQAccount):
    """Print lamp information and turn on/off if requested

    Args:
        account (MyQAccount): Account for which to retrieve lamps
    """
    print(f"  Lamps: {len(account.lamps)}")
    print("  ---------")
    if len(account.lamps) != 0:
        for idx, device in enumerate(account.lamps.values()):
            print_info(number=idx, device=device)

            if ISSUE_COMMANDS:
                try:
                    print(f"Turning lamp {device.name} on")
                    await device.turnon(wait_for_state=True)
                    await asyncio.sleep(5)
                    print(f"Turning lamp {device.name} off")
                    await device.turnoff(wait_for_state=True)
                except RequestError as err:
                    _LOGGER.error(err)
        print("  ------------------------------")


async def print_gateways(account: MyQAccount):
    """Print gateways for account

    Args:
        account (MyQAccount): Account for which to retrieve gateways
    """
    print(f"  Gateways: {len(account.gateways)}")
    print("  ------------")
    if len(account.gateways) != 0:
        for idx, device in enumerate(account.gateways.values()):
            print_info(number=idx, device=device)

    print("------------------------------")


async def print_other(account: MyQAccount):
    """Print unknown/other devices for account

    Args:
        account (MyQAccount): Account for which to retrieve unknown devices
    """
    print(f"  Other: {len(account.other)}")
    print("  ------------")
    if len(account.other) != 0:
        for idx, device in enumerate(account.other.values()):
            print_info(number=idx, device=device)

    print("------------------------------")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.DEBUG)
    async with ClientSession() as websession:
        try:
            # Create an API object:
            print(f"{EMAIL} {PASSWORD}")
            api = await login(EMAIL, PASSWORD, websession)

            for account in api.accounts.values():
                print(f"Account ID: {account.id}")
                print(f"Account Name: {account.name}")

                # Get all devices listed with this account – note that you can use
                # api.covers to only examine covers or api.lamps for only lamps.
                await print_garagedoors(account=account)

                await print_lamps(account=account)

                await print_gateways(account=account)

        except MyQError as err:
            _LOGGER.error("There was an error: %s", err)


asyncio.get_event_loop().run_until_complete(main())
