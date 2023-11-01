from decimal import Decimal
from dao_indexer import models as models
from dao_indexer.types.dao_governance.tezos_big_maps.governance_parameters_key import GovernanceParametersKey
from dao_indexer.types.dao_governance.tezos_big_maps.governance_parameters_value import GovernanceParametersValue
from dipdup.context import HandlerContext
from dipdup.models.tezos_tzkt import TzktBigMapDiff


async def on_update_governance_parameters(
    ctx: HandlerContext,
    governance_parameters: TzktBigMapDiff[GovernanceParametersKey, GovernanceParametersValue],
) -> None:
    # Return if we have nothing to update
    if not governance_parameters.action.has_value:
        return

    # Create a new governance parameters entry
    gpData = governance_parameters.value
    gp = await models.GovernanceParameters.create(
        id=governance_parameters.key.__root__,
        vote_method=models.VoteMethod[list(gpData.vote_method.__dict__.keys())[0]],
        vote_period=gpData.vote_period,
        wait_period=gpData.wait_period,
        escrow_amount=gpData.escrow_amount,
        escrow_return=Decimal(gpData.escrow_return) / 100,
        min_amount=gpData.min_amount,
        supermajority=Decimal(gpData.supermajority) / 100,
        representatives_share=Decimal(gpData.representatives_share) / 100,
        representative_max_share=Decimal(gpData.representative_max_share) / 100,
        quorum_update_period=gpData.quorum_update_period,
        quorum_update=Decimal(gpData.quorum_update) / 100,
        quorum_max_change=Decimal(gpData.quorum_max_change) / 100,
        min_quorum=gpData.min_quorum,
        max_quorum=gpData.max_quorum
    )

    # Print some log information
    ctx.logger.info(gp)
