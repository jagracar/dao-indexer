from decimal import Decimal
from dao_indexer import models as models
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktTokenBalanceData


async def on_balance_update(
    ctx: HandlerContext,
    token_balance: TzktTokenBalanceData,
) -> None:
    member, _ = await models.Member.update_or_create(
        address=token_balance.account_address,
        defaults={
            'token_balance': Decimal(token_balance.balance) / 10**6
        }
    )

    # Print some log information
    #ctx.logger.info(member)
