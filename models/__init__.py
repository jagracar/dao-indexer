import enum

from dipdup import fields
from dipdup.models import Model

class Proposal(Model):
    id = fields.TextField(pk=True)

    title: fields.TextField()
    description: fields.TextField()
    issuer: fields.TextField()
    level: fields.IntField()
    quorum: fields.IntField()

