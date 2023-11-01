from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.token_votes_key import TokenVotesKey
from dao_indexer.types.dao_governance.tezos_big_maps.token_votes_value import TokenVotesValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_token_votes(
    ctx: HandlerContext,
    token_votes: TzktBigMapDiff[TokenVotesKey, TokenVotesValue],
) -> None:
    # Return if we have nothing to update
    if not token_votes.action.has_value:
        return

    # Get the associated member
    address = token_votes.key.address
    member, _  = await models.Member.get_or_create(address=address)

    # Get the associated proposal
    proposalId = token_votes.key.nat
    proposal = await models.Proposal.get(id=proposalId)

    # Create a new member vote entry
    vote = await models.MemberVote.create(
        id="%s_%s" % (address, proposalId),
        member=member,
        proposal=proposal,
        vote=models.VoteKind(list(token_votes.value.vote.__dict__.keys())[0]),
        weight=token_votes.value.weight
    )

    # Print some log information
    ctx.logger.info(vote)
