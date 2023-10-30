from dipdup import fields
from dipdup.models import Model


class Proposal(Model):
    id = fields.TextField(pk=True)
    title = fields.TextField()
    description = fields.TextField()
    issuer = fields.TextField()
    timestamp = fields.DatetimeField()
    level = fields.BigIntField()
    quorum = fields.BigIntField()
    token_votes_total = fields.BigIntField()
    representatives_votes_total = fields.BigIntField()
    vote_ends = fields.DatetimeField()
    wait_ends = fields.DatetimeField()

    def __str__(self):
        return "Proposal %s: %s" % (self.id, self.title)


class GovernanceParameters(Model):
    id = fields.TextField(pk=True)
    vote_period = fields.IntField()
    wait_period = fields.IntField()
    escrow_amount = fields.BigIntField()
    escrow_return = fields.FloatField()
    min_amount = fields.BigIntField()
    supermajority = fields.FloatField()
    representatives_share = fields.FloatField()
    representative_max_share = fields.FloatField()
    quorum_update_period = fields.IntField()
    quorum_update = fields.FloatField()
    quorum_max_change = fields.FloatField()
    min_quorum = fields.BigIntField()
    max_quorum = fields.BigIntField()

    def __str__(self):
        return "Governance parameters %s" % self.id
