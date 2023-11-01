from enum import Enum
from dipdup import fields
from dipdup.models import Model


class VoteMethod(Enum):
    LINEAR = 'linear'
    QUADRATIC = 'quadratic'


class ProposalKind(Enum):
    TEXT = 'text'
    TRANSFER_MUTEZ = 'transfer_mutez'
    TRANSFER_TOKEN = 'transfer_token'
    LAMBDA_FUNCTION = 'lambda_function'


class ProposalStatus(Enum):
    OPEN = 'open'
    CANCELLED = 'cancelled'
    APPROVED = 'approved'
    EXECUTED = 'executed'
    REJECTED = 'rejected'


class VoteKind(Enum):
    YES = 'yes'
    NO = 'no'
    ABSTAIN = 'abstain'


class Member(Model):
    address = fields.TextField(pk=True)
    alias = fields.TextField(default='')
    token_balance = fields.DecimalField(decimal_places=6, max_digits=12, default=0)

    def __str__(self):
        return "DAO member %s, %s TEIA" % (
            self.alias if self.alias != '' else self.address, self.token_balance)


class Community(Model):
    id = fields.TextField(pk=True)


class GovernanceParameters(Model):
    id = fields.IntField(pk=True)
    vote_method = fields.EnumField(enum_type=VoteMethod)
    vote_period = fields.TimeDeltaField()
    wait_period = fields.TimeDeltaField()
    escrow_amount = fields.BigIntField()
    escrow_return = fields.DecimalField(decimal_places=2, max_digits=3)
    min_amount = fields.BigIntField()
    supermajority = fields.DecimalField(decimal_places=2, max_digits=3)
    representatives_share = fields.DecimalField(decimal_places=2, max_digits=3)
    representative_max_share = fields.DecimalField(decimal_places=2, max_digits=3)
    quorum_update_period = fields.TimeDeltaField()
    quorum_update = fields.DecimalField(decimal_places=2, max_digits=3)
    quorum_max_change = fields.DecimalField(decimal_places=2, max_digits=3)
    min_quorum = fields.BigIntField()
    max_quorum = fields.BigIntField()

    def __str__(self):
        return "Governance parameters %s" % self.id


class Proposal(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    description = fields.TextField()
    kind = fields.EnumField(enum_type=ProposalKind)
    issuer: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'submited_proposals')
    timestamp = fields.DatetimeField()
    voting_end = fields.DatetimeField()
    waiting_end = fields.DatetimeField()
    level = fields.BigIntField()
    quorum = fields.BigIntField()
    gp: fields.ForeignKeyField[GovernanceParameters] = fields.ForeignKeyField(
        'models.GovernanceParameters', 'proposals')
    status = fields.EnumField(enum_type=ProposalStatus)
    token_votes_summary = fields.JSONField()
    representatives_votes_summary = fields.JSONField()

    def __str__(self):
        return "Proposal %i: %s" % (self.id, self.title)


class MemberVote(Model):
    id = fields.TextField(pk=True)
    member: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'token_votes')
    vote = fields.EnumField(enum_type=VoteKind)
    weight = fields.BigIntField()

    def __str__(self):
        username = self.member.alias if self.member.alias != '' else self.member.address 
        return "%s voted %s in proposal %s" % (
            username, self.vote, self.proposal.id)


class RepresentativeVote(Model):
    id = fields.TextField(pk=True)
    community: fields.ForeignKeyField[Community] = fields.ForeignKeyField(
        'models.Community', 'votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'representatives_votes')
    vote = fields.EnumField(enum_type=VoteKind)

    def __str__(self):
        return "%s voted %s in proposal %s" % (
            self.community.id, self.vote, self.proposal.id)
