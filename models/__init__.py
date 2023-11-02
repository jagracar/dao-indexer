from enum import Enum
from dipdup import fields
from dipdup.models import Model


class ProposalVoteWeightMethod(Enum):
    LINEAR = 'linear'
    QUADRATIC = 'quadratic'


class PollVoteWeightMethod(Enum):
    EQUAL = 'equal'
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
    address = fields.CharField(36, pk=True)
    alias = fields.TextField(default='')
    token_balance = fields.DecimalField(decimal_places=6, max_digits=12, default=0)
    n_token_checkpoints = fields.BigIntField(default=0)
    n_submitted_proposals = fields.IntField(default=0)
    n_voted_proposals = fields.IntField(default=0)
    n_submitted_polls = fields.IntField(default=0)
    n_voted_polls = fields.IntField(default=0)

    def __str__(self):
        username = self.alias if self.alias != '' else self.address
        return "%s (%.1f TEIA)" % (username, self.token_balance)


class Community(Model):
    id = fields.TextField(pk=True)
    n_voted_proposals = fields.IntField(default=0)

    def __str__(self):
        return "%s" % self.id


class GovernanceParameters(Model):
    id = fields.IntField(pk=True)
    vote_method = fields.EnumField(enum_type=ProposalVoteWeightMethod)
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
        return "governance parameters %i" % self.id


class Proposal(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    description = fields.TextField()
    kind = fields.EnumField(enum_type=ProposalKind)
    content = fields.JSONField()
    issuer: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'submitted_proposals')
    timestamp = fields.DatetimeField()
    vote_end_timestamp = fields.DatetimeField()
    wait_end_timestamp = fields.DatetimeField()
    level = fields.BigIntField()
    quorum = fields.BigIntField()
    gp: fields.ForeignKeyField[GovernanceParameters] = fields.ForeignKeyField(
        'models.GovernanceParameters', 'proposals')
    status = fields.EnumField(enum_type=ProposalStatus)
    token_votes_summary = fields.JSONField()
    representatives_votes_summary = fields.JSONField()

    def __str__(self):
        return "proposal %i (%s)" % (self.id, self.title)


class MemberVote(Model):
    id = fields.TextField(pk=True)
    member: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'proposal_votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'token_votes')
    vote = fields.EnumField(enum_type=VoteKind)
    weight = fields.BigIntField()
    timestamp = fields.DatetimeField()

    def __str__(self):
        [address, proposalId] = self.id.split("_")
        return "%s voted %s in proposal %s" % (
            address, self.vote.value, proposalId)


class RepresentativeVote(Model):
    id = fields.TextField(pk=True)
    community: fields.ForeignKeyField[Community] = fields.ForeignKeyField(
        'models.Community', 'proposal_votes')
    proposal: fields.ForeignKeyField[Proposal] = fields.ForeignKeyField(
        'models.Proposal', 'representatives_votes')
    vote = fields.EnumField(enum_type=VoteKind)
    timestamp = fields.DatetimeField()

    def __str__(self):
        [community, proposalId] = self.id.split("_")
        return "%s voted %s in proposal %s" % (
            community, self.vote.value, proposalId)


class Poll(Model):
    id = fields.IntField(pk=True)
    question = fields.TextField()
    description = fields.TextField()
    options = fields.JSONField()
    vote_weight_method = fields.EnumField(enum_type=PollVoteWeightMethod)
    issuer: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'submitted_polls')
    timestamp = fields.DatetimeField()
    vote_end_timestamp = fields.DatetimeField()
    level = fields.BigIntField()
    votes_summary = fields.JSONField()

    def __str__(self):
        return "poll %i (%s)" % (self.id, self.question)


class PollVote(Model):
    id = fields.TextField(pk=True)
    member: fields.ForeignKeyField[Member] = fields.ForeignKeyField(
        'models.Member', 'poll_votes')
    poll: fields.ForeignKeyField[Poll] = fields.ForeignKeyField(
        'models.Poll', 'votes')
    option = fields.IntField()
    weight = fields.BigIntField()
    timestamp = fields.DatetimeField()

    def __str__(self):
        [address, pollId] = self.id.split("_")
        return "%s voted option '%s' in poll %s" % (
            address, self.option, pollId)
