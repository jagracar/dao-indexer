from datetime import datetime, timedelta
from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_key import ProposalsKey
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_value import ProposalsValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_proposals(
    ctx: HandlerContext,
    proposals: TzktBigMapDiff[ProposalsKey, ProposalsValue],
) -> None:
    # Return if we have nothing to update
    if not proposals.action.has_value:
        return

    # Get the proposal id and the updated data
    proposalId = proposals.key.__root__
    proposalData = proposals.value

    # Update the proposal or create a new one
    proposal = await models.Proposal.get_or_none(id=proposalId)

    if proposal:
        await proposal.update_from_dict({
            'token_votes_total': proposalData.token_votes.total,
            'representatives_votes_total': proposalData.representatives_votes.total
        }).save()
    else:
        # Get the associated governance parameters
        gp = await models.GovernanceParameters.get(id=proposalData.gp_index)

        # Create a new proposal entry
        timestamp = datetime.fromisoformat(proposalData.timestamp)
        proposal = await models.Proposal.create(
            id=proposalId,
            title=bytes.fromhex(proposalData.title).decode(),
            description=bytes.fromhex(proposalData.description).decode(),
            issuer=proposalData.issuer,
            timestamp=timestamp,
            level=proposalData.level,
            quorum=proposalData.quorum,
            token_votes_total=proposalData.token_votes.total,
            representatives_votes_total=proposalData.representatives_votes.total,
            vote_ends=timestamp + timedelta(days=int(gp.vote_period)),
            wait_ends=timestamp + timedelta(days=(int(gp.vote_period) + int(gp.wait_period))),
        )

    ctx.logger.info(proposal)
