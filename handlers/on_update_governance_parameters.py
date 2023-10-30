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
        vote_period=gpData.vote_period,
        wait_period=gpData.wait_period,
        escrow_amount=gpData.escrow_amount,
        escrow_return=float(gpData.escrow_return) / 100,
        min_amount=gpData.min_amount,
        supermajority=float(gpData.supermajority) / 100,
        representatives_share=float(gpData.representatives_share) / 100,
        representative_max_share=float(gpData.representative_max_share) / 100,
        quorum_update_period=gpData.quorum_update_period,
        quorum_update=float(gpData.quorum_update) / 100,
        quorum_max_change=float(gpData.quorum_max_change) / 100,
        min_quorum=gpData.min_quorum,
        max_quorum=gpData.max_quorum)

    ctx.logger.info(gp)
