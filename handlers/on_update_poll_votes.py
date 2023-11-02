from dao_indexer import models as models
from dao_indexer.types.dao_polls.tezos_big_maps.votes_key import VotesKey
from dao_indexer.types.dao_polls.tezos_big_maps.votes_value import VotesValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_poll_votes(
    ctx: HandlerContext,
    votes: TzktBigMapDiff[VotesKey, VotesValue],
) -> None:
    # Return if we have nothing to update
    if not votes.action.has_value:
        return

    # Update the poll vote or create a new one
    address = votes.key.address
    pollId = votes.key.nat
    voteId = "%s_%s" % (address, pollId)
    vote = await models.PollVote.get_or_none(id=voteId)

    if vote:
        # Update the poll vote
        await vote.update_from_dict({
            'option': votes.value.option,
            'timestamp': votes.data.timestamp
        }).save()
    else:
        # Get the associated member and update their voted polls counter
        member = await models.Member.get(address=address)
        member.n_voted_polls += 1
        await member.save()

        # Get the associated poll
        poll = await models.Poll.get(id=pollId)

        # Create a new poll vote entry
        vote = await models.PollVote.create(
            id=voteId,
            member=member,
            poll=poll,
            option=votes.value.option,
            weight=votes.value.weight,
            timestamp=votes.data.timestamp
        )

        # Print some log information
        ctx.logger.info(
            "%s voted option '%s' in proposal %s",
            member, vote.option, pollId
        )
