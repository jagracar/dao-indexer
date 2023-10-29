from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_key import ProposalsKey
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_value import ProposalsValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_proposals(
    ctx: HandlerContext,
    proposals: TzktBigMapDiff[ProposalsKey, ProposalsValue],
) -> None:
    if not proposals.action.has_value:
        return
    assert proposals.key
    assert proposals.value

    ctx.logger.info('Processing proposal with title `%s`', bytes.fromhex(proposals.value.title).decode())

    await models.Proposal.update_or_create(
        id=proposals.key.__root__, 
        defaults={
            'title': bytes.fromhex(proposals.value.title).decode(),
            'description': bytes.fromhex(proposals.value.description).decode(),
            'issuer': proposals.value.issuer,
            'level': int(proposals.value.level),
            'quorum': int(proposals.value.quorum)})
