from dao_indexer import models as models
from dao_indexer.handlers import utils
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

    # Get the associated community and update their voted proposals counter
    communityId = representatives_votes.key.string
    community, _  = await models.Community.get_or_create(id=communityId)
    community.n_voted_proposals += 1
    await community.save()

    # Get the associated proposal
    proposalId = representatives_votes.key.nat
    proposal = await models.Proposal.get(id=proposalId)

    # Create a new representative vote entry
    vote = await models.RepresentativeVote.create(
        id="%s_%s" % (communityId, proposalId),
        community=community,
        proposal=proposal,
        vote=models.VoteKind(utils.first_key(representatives_votes.value.__root__.dict())),
        timestamp=representatives_votes.data.timestamp
    )

    # Print some log information
    ctx.logger.info(
        "%s voted option '%s' in proposal %s",
        community, vote.vote.value, proposalId
    )
