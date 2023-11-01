from enum import IntEnum
from dipdup import fields
from dipdup.models import Model


class ProposalKind(IntEnum):
    text = 0
    transfer_mutez = 1
    transfer_token = 2
    lambda_function = 3


class ProposalStatus(IntEnum):
    open = 0
    cancelled = 1
    approved = 2
    executed = 3
    rejected = 4


class VoteMethod(IntEnum):
    linear = 0
    quadratic = 1


class VoteKind(IntEnum):
    yes = 0
    no = 1
    abstain = 1


class Member(Model):
    address = fields.TextField(pk=True)


class Community(Model):
    id = fields.TextField(pk=True)


class GovernanceParameters(Model):
    id = fields.IntField(pk=True)
    vote_method = fields.IntEnumField(enum_type=VoteMethod)
    vote_period = fields.IntField()
    wait_period = fields.IntField()
    escrow_amount = fields.BigIntField()
    escrow_return = fields.DecimalField(decimal_places=2, max_digits=3)
    min_amount = fields.BigIntField()
    supermajority = fields.DecimalField(decimal_places=2, max_digits=3)
    representatives_share = fields.DecimalField(decimal_places=2, max_digits=3)
    representative_max_share = fields.DecimalField(decimal_places=2, max_digits=3)
    quorum_update_period = fields.IntField()
    quorum_update = fields.DecimalField(decimal_places=2, max_digits=3)
    quorum_max_change = fields.DecimalField(decimal_places=2, max_digits=3)
    min_quorum = fields.BigIntField()
    max_quorum = fields.BigIntField()

    def __str__(self):
        return "Governance parameters %s" % self.id


class TokenVotesSummary(Model):
    proposal_id = fields.IntField(pk=True)
    positive = fields.BigIntField()
    negative = fields.BigIntField()
    abstain = fields.BigIntField()
    total = fields.BigIntField()
    participation = fields.IntField()


class RepresentativesVotesSummary(Model):
    proposal_id = fields.IntField(pk=True)
    positive = fields.BigIntField()
    negative = fields.BigIntField()
    abstain = fields.BigIntField()
    total = fields.BigIntField()
    participation = fields.IntField()


class Proposal(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    description = fields.TextField()
    kind = fields.IntEnumField(enum_type=ProposalKind)
    issuer: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'submited_proposals')
    timestamp = fields.DatetimeField()
    voting_end = fields.DatetimeField()
    waiting_end = fields.DatetimeField()
    level = fields.BigIntField()
    quorum = fields.BigIntField()
    gp: fields.ForeignKeyField[GovernanceParameters] = fields.ForeignKeyField(
        'models.GovernanceParameters', 'proposals')
    status = fields.IntEnumField(enum_type=ProposalStatus)
    token_votes_summary: fields.ForeignKeyField[TokenVotesSummary] = fields.ForeignKeyField(
        'models.TokenVotesSummary', 'proposals')
    representatives_votes_summary: fields.ForeignKeyField[RepresentativesVotesSummary] = fields.ForeignKeyField(
        'models.RepresentativesVotesSummary', 'proposals')

    def __str__(self):
        return "Proposal %i: %s" % (self.id, self.title)


class MemberVote(Model):
    id = fields.TextField(pk=True)
    member: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'token_votes')
    vote = fields.IntEnumField(enum_type=VoteKind)
    weight = fields.BigIntField()

    def __str__(self):
        return "%s voted %i in proposal %s" % (
            self.member.address, self.vote, self.proposal.id)


class RepresentativeVote(Model):
    id = fields.TextField(pk=True)
    community: fields.ForeignKeyField[Community] = fields.ForeignKeyField(
        'models.Community', 'votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'representatives_votes')
    vote = fields.IntEnumField(enum_type=VoteKind)

    def __str__(self):
        return "%s voted %i in proposal %s" % (
            self.community.id, self.vote, self.proposal.id)
