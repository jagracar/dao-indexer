from datetime import datetime, timedelta
from dao_indexer import models as models
from dao_indexer.handlers import utils
from dao_indexer.types.dao_polls.tezos_big_maps.polls_key import PollsKey
from dao_indexer.types.dao_polls.tezos_big_maps.polls_value import PollsValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_polls(
    ctx: HandlerContext,
    polls: TzktBigMapDiff[PollsKey, PollsValue],
) -> None:
    # Return if we have nothing to update
    if not polls.action.has_value:
        return

    # Get the poll id and the updated data
    pollId = polls.key.__root__
    pollData = polls.value
    votes_summary = pollData.votes_count

    # Update the poll or create a new one
    poll = await models.Poll.get_or_none(id=pollId)

    if poll:
        # Update the poll
        await poll.update_from_dict({
            'votes_summary': votes_summary
        }).save()
    else:
        # Get the poll issuer and update the submitted polls counter
        issuer = await models.Member.get(address=pollData.issuer)
        issuer.n_submitted_polls += 1
        await issuer.save()

        # Create a new poll entry
        timestamp = datetime.fromisoformat(pollData.timestamp)
        poll = await models.Poll.create(
            id=pollId,
            question=utils.hex_to_utf8(pollData.question),
            description=utils.hex_to_utf8(pollData.description),
            options={key: utils.hex_to_utf8(value) for key, value in pollData.options.items()},
            vote_weight_method=models.PollVoteWeightMethod(utils.first_key(pollData.vote_weight_method.dict())),
            issuer=issuer,
            timestamp=timestamp,
            vote_end_timestamp=timestamp + timedelta(days=int(pollData.vote_period)),
            level=pollData.level,
            votes_summary=votes_summary
        )

        # Print some log information
        ctx.logger.info("%s created a new poll: %s", issuer, poll.question)
