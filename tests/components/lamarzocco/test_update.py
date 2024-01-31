"""Tests for the La Marzocco Update Entities."""


from unittest.mock import MagicMock

from lmcloud.const import LaMarzoccoUpdateableComponent
import pytest
from syrupy import SnapshotAssertion

from homeassistant.components.update import DOMAIN as UPDATE_DOMAIN, SERVICE_INSTALL
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

pytestmark = pytest.mark.usefixtures("init_integration")


@pytest.mark.parametrize(
    ("entity_name", "component"),
    [
        ("machine_firmware", LaMarzoccoUpdateableComponent.MACHINE),
        ("gateway_firmware", LaMarzoccoUpdateableComponent.GATEWAY),
    ],
)
async def test_update_entites(
    hass: HomeAssistant,
    mock_lamarzocco: MagicMock,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    entity_name: str,
    component: LaMarzoccoUpdateableComponent,
) -> None:
    """Test the La Marzocco update entities."""

    serial_number = mock_lamarzocco.serial_number

    state = hass.states.get(f"update.{serial_number}_{entity_name}")
    assert state
    assert state == snapshot

    entry = entity_registry.async_get(state.entity_id)
    assert entry
    assert entry == snapshot

    await hass.services.async_call(
        UPDATE_DOMAIN,
        SERVICE_INSTALL,
        {
            ATTR_ENTITY_ID: f"update.{serial_number}_{entity_name}",
        },
        blocking=True,
    )

    mock_lamarzocco.update_firmware.assert_called_once_with(component)


async def test_update_error(
    hass: HomeAssistant,
    mock_lamarzocco: MagicMock,
) -> None:
    """Test error during update."""
    state = hass.states.get(f"update.{mock_lamarzocco.serial_number}_machine_firmware")
    assert state

    mock_lamarzocco.update_firmware.return_value = False

    with pytest.raises(HomeAssistantError, match="Update failed"):
        await hass.services.async_call(
            UPDATE_DOMAIN,
            SERVICE_INSTALL,
            {
                ATTR_ENTITY_ID: f"update.{mock_lamarzocco.serial_number}_machine_firmware",
            },
            blocking=True,
        )
