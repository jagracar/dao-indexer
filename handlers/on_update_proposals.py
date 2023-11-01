from datetime import datetime
from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_key import ProposalsKey
from dao_indexer.types.dao_governance.tezos_big_maps.proposals_value import ProposalsValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


def to_int_dictionary(instance):
    return {key: int(value) for key, value in instance.__dict__.items()}


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
    status = models.ProposalStatus(list(proposalData.status.__dict__.keys())[0])
    token_votes_summary = to_int_dictionary(proposalData.token_votes)
    representatives_votes_summary = to_int_dictionary(proposalData.representatives_votes)

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
        # Get the proposal issuer
        issuer, _ = await models.Member.get_or_create(address=proposalData.issuer)

        # Get the associated governance parameters
        gp = await models.GovernanceParameters.get(id=proposalData.gp_index)

        # Create a new proposal entry
        timestamp = datetime.fromisoformat(proposalData.timestamp)
        proposal = await models.Proposal.create(
            id=proposalId,
            title=bytes.fromhex(proposalData.title).decode(),
            description=bytes.fromhex(proposalData.description).decode(),
            kind=models.ProposalKind(list(proposalData.kind.__dict__.keys())[0]),
            issuer=issuer,
            timestamp=timestamp,
            voting_end=timestamp + gp.vote_period,
            waiting_end=timestamp + gp.vote_period + gp.wait_period,
            level=proposalData.level,
            quorum=proposalData.quorum,
            gp=gp,
            status=status,
            token_votes_summary=token_votes_summary,
            representatives_votes_summary=representatives_votes_summary
        )

    # Print some log information
    ctx.logger.info(proposal)
