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
        # Update the token votes summary
        token_votes_summary = await proposal.token_votes_summary
        await token_votes_summary.update_from_dict(
            proposalData.token_votes.__dict__
        ).save()

        # Update the representatives votes summary
        representatives_votes_summary = await proposal.representatives_votes_summary
        await representatives_votes_summary.update_from_dict(
            proposalData.representatives_votes.__dict__
        ).save()

        # Update the proposal
        await proposal.update_from_dict({
            'status': models.ProposalStatus[list(proposalData.status.__dict__.keys())[0]]
        }).save()
    else:
        # Get the proposal issuer
        issuer, _ = await models.Member.get_or_create(address=proposalData.issuer)

        # Get the associated governance parameters
        gp = await models.GovernanceParameters.get(id=proposalData.gp_index)

        # Create the token votes summary entry
        token_votes_summary = await models.TokenVotesSummary.create(
            proposal_id=proposalId,
            **proposalData.token_votes.__dict__
        )

        # Create the representatives votes summary entry
        representatives_votes_summary = await models.RepresentativesVotesSummary.create(
            proposal_id=proposalId,
            **proposalData.representatives_votes.__dict__
        )

        # Create a new proposal entry
        timestamp = datetime.fromisoformat(proposalData.timestamp)
        proposal = await models.Proposal.create(
            id=proposalId,
            title=bytes.fromhex(proposalData.title).decode(),
            description=bytes.fromhex(proposalData.description).decode(),
            kind=models.ProposalKind[list(proposalData.kind.__dict__.keys())[0]],
            issuer=issuer,
            timestamp=timestamp,
            voting_end=timestamp + timedelta(days=int(gp.vote_period)),
            waiting_end=timestamp + timedelta(days=(int(gp.vote_period) + int(gp.wait_period))),
            level=proposalData.level,
            quorum=proposalData.quorum,
            gp=gp,
            status=models.ProposalStatus[list(proposalData.status.__dict__.keys())[0]],
            token_votes_summary=token_votes_summary,
            representatives_votes_summary=representatives_votes_summary,
        )

    # Print some log information
    ctx.logger.info(proposal)
