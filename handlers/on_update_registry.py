from dao_indexer import models as models
from dao_indexer.handlers import utils
from dao_indexer.types.hen_subjkt.tezos_big_maps.registries_key import RegistriesKey
from dao_indexer.types.hen_subjkt.tezos_big_maps.registries_value import RegistriesValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_registry(
    ctx: HandlerContext,
    registries: TzktBigMapDiff[RegistriesKey, RegistriesValue],
) -> None:
    # Return if we have nothing to update
    if not registries.action.has_value:
        return

    # Update the member alias
    await models.Member.update_or_create(
        address=registries.key.__root__,
        defaults={
            'alias': utils.hex_to_utf8(registries.value.__root__)
        }
    )
