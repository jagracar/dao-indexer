from dao_indexer import models as models
from dao_indexer.types.dao_token.tezos_big_maps.n_checkpoints_key import NCheckpointsKey
from dao_indexer.types.dao_token.tezos_big_maps.n_checkpoints_value import NCheckpointsValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_n_checkpoints(
    ctx: HandlerContext,
    n_checkpoints: TzktBigMapDiff[NCheckpointsKey, NCheckpointsValue],
) -> None:
    # Return if we have nothing to update
    if not n_checkpoints.action.has_value:
        return

    # Update the member or create a new one
    await models.Member.update_or_create(
        address=n_checkpoints.key.__root__,
        defaults={
            'n_token_checkpoints': n_checkpoints.value.__root__
        }
    )
