from datetime import datetime
from dao_indexer import models as models
from dao_indexer.handlers import utils
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
    status = models.ProposalStatus(utils.first_key(proposalData.status.dict()))
    token_votes_summary = proposalData.token_votes.dict()
    representatives_votes_summary = proposalData.representatives_votes.dict()

    # Update the proposal or create a new one
    proposal = await models.Proposal.get_or_none(id=proposalId)

    if proposal:
        # Update the proposal
        await proposal.update_from_dict({
            'status': status,
            'token_votes_summary': token_votes_summary,
            'representatives_votes_summary': representatives_votes_summary
        }).save()
    else:
        # Get the proposal issuer and update the submitted proposals counter
        issuer = await models.Member.get(address=proposalData.issuer)
        issuer.n_submitted_proposals += 1
        await issuer.save()

        # Get the associated governance parameters
        gp = await models.GovernanceParameters.get(id=proposalData.gp_index)

        # Create a new proposal entry
        timestamp = datetime.fromisoformat(proposalData.timestamp)
        proposal = await models.Proposal.create(
            id=proposalId,
            title=utils.hex_to_utf8(proposalData.title),
            description=utils.hex_to_utf8(proposalData.description),
            kind=models.ProposalKind(utils.first_key(proposalData.kind.dict())),
            content=utils.first_value(proposalData.kind.dict()),
            issuer=issuer,
            timestamp=timestamp,
            vote_end_timestamp=timestamp + gp.vote_period,
            wait_end_timestamp=timestamp + gp.vote_period + gp.wait_period,
            level=proposalData.level,
            quorum=proposalData.quorum,
            gp=gp,
            status=status,
            token_votes_summary=token_votes_summary,
            representatives_votes_summary=representatives_votes_summary
        )

        # Print some log information
        ctx.logger.info(
            "%s submitted a new proposal: %s",
            issuer, proposal.title
        )
