from decimal import Decimal
from dao_indexer import models as models
from dao_indexer.types.dao_token.tezos_big_maps.ledger_key import LedgerKey
from dao_indexer.types.dao_token.tezos_big_maps.ledger_value import LedgerValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_ledger(
    ctx: HandlerContext,
    ledger: TzktBigMapDiff[LedgerKey, LedgerValue],
) -> None:
    # Return if we have nothing to update
    if not ledger.action.has_value:
        return

    # Update the member or create a new one
    await models.Member.update_or_create(
        address=ledger.key.__root__,
        defaults={
            'token_balance': Decimal(ledger.value.__root__) / 10**6
        }
    )
