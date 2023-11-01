from dao_indexer import models as models
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
    alias = ''

    try:
        alias = bytes.fromhex(registries.value.__root__).decode()
    except:
        ctx.logger.info("Problem decoding user alias %s" % registries.value.__root__)

    member, _ = await models.Member.update_or_create(
        address=registries.key.__root__,
        defaults={
            'alias': alias
        }
    )

    # Print some log information
    #ctx.logger.info(member)
