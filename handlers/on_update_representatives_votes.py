from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.representatives_votes_key import RepresentativesVotesKey
from dao_indexer.types.dao_governance.tezos_big_maps.representatives_votes_value import RepresentativesVotesValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_representatives_votes(
    ctx: HandlerContext,
    representatives_votes: TzktBigMapDiff[RepresentativesVotesKey, RepresentativesVotesValue],
) -> None:
    # Return if we have nothing to update
    if not representatives_votes.action.has_value:
        return

    # Get the associated community
    communityId = representatives_votes.key.string
    community, _  = await models.Community.get_or_create(id=communityId)

    # Get the associated proposal
    proposalId = representatives_votes.key.nat
    proposal = await models.Proposal.get(id=proposalId)

    # Create a new representative vote entry
    vote = await models.RepresentativeVote.create(
        id="%s_%s" % (communityId, proposalId),
        community=community,
        proposal=proposal,
        vote=models.VoteKind[list(representatives_votes.value.__root__.__dict__.keys())[0]],
    )

    # Print some log information
    ctx.logger.info(vote)
