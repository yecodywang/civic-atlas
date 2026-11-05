"""Data model for the civic-atlas catalog.

These Pydantic models are the single source of truth for the catalog format. The JSON Schema files
in ``schema/`` are generated from them (``civic-atlas schema``), so contributors get editor
autocomplete while the Python code and the schema never drift apart.

Three kinds of YAML file live under ``jurisdictions/``:

* ``<jurisdiction>/jurisdiction.yaml``: a :class:`Jurisdiction`
* ``<jurisdiction>/services/<service-id>.yaml``: a :class:`Service`
* ``<jurisdiction>/routing.yaml`` (optional): a :class:`Routing` table for "who do I contact?"

A jurisdiction's id is its folder path (for example ``us/nc/place/raleigh``). It is not written
inside the file. See ``docs/data-model.md``.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl, model_validator

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
PHONE_PATTERN = r"^[0-9+() .\-]+$"
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"


def _number_to_text(value: Any) -> Any:
    """YAML reads bare 211, 311 or 911 as numbers; accept them wherever text is expected."""
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return value


Text = Annotated[str, BeforeValidator(_number_to_text)]
"""A string that also accepts a bare YAML number, such as ``911``."""


class _Strict(BaseModel):
    """Base model: unknown keys are errors, so typos in YAML are caught."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class JurisdictionKind(StrEnum):
    COUNTRY = "country"
    STATE = "state"
    COUNTY = "county"
    PLACE = "place"
    DISTRICT = "district"


class Category(StrEnum):
    """Task-menu groups, from the "Raleigh at Your Fingertips" curriculum."""

    FIX_REPORT = "fix-report"
    PAY_MANAGE = "pay-manage"
    STAY_INFORMED = "stay-informed"
    FIND_HELP = "find-help"
    HAVE_A_SAY = "have-a-say"
    CONTACT = "contact"


class CoreSkill(StrEnum):
    """The four core skills that open the door to most services."""

    KNOW_WHO = "know-who"
    REPORT_REQUEST = "report-request"
    STAY_INFORMED = "stay-informed"
    ACCOUNTS_PAYMENTS = "accounts-payments"


class ChannelType(StrEnum):
    WEB = "web"
    PHONE = "phone"
    TEXT = "text"
    APP = "app"
    EMAIL = "email"
    IN_PERSON = "in-person"


class ProviderType(StrEnum):
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"
    OTHER = "other"


class Status(StrEnum):
    DRAFT = "draft"
    """Compiled from official sources but not yet checked by a human volunteer."""
    VERIFIED = "verified"
    """A named person checked every fact against the official source on ``verified_on``."""
    NEEDS_REVIEW = "needs-review"
    """Reported or suspected to be out of date. Treat with caution."""


class Provenance(_Strict):
    """Where an entry's facts came from and how fresh they are. Required on every entry."""

    source_urls: list[HttpUrl] = Field(
        min_length=1, description="Official pages the facts in this entry were taken from."
    )
    last_checked: date = Field(
        description="Date someone last compared this entry against its sources (YYYY-MM-DD)."
    )
    status: Status = Field(default=Status.DRAFT)
    verified_by: str | None = Field(
        default=None, description="GitHub handle of the human who verified the entry."
    )
    verified_on: date | None = None
    notes: str | None = Field(default=None, description="Caveats about the sources.")

    @model_validator(mode="after")
    def _verified_needs_a_person(self) -> Provenance:
        if self.status is Status.VERIFIED and not (self.verified_by and self.verified_on):
            raise ValueError("status 'verified' requires verified_by and verified_on")
        return self


class Channel(_Strict):
    """One way to reach a service: a website, phone number, app, and so on."""

    type: ChannelType
    label: str = Field(description="Short human label, e.g. 'Ask Raleigh website'.")
    url: HttpUrl | None = None
    phone: Text | None = Field(default=None, pattern=PHONE_PATTERN)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN)
    hours: str | None = None
    purpose: str | None = Field(default=None, description="When to use this channel.")
    notes: str | None = None

    @model_validator(mode="after")
    def _has_an_address(self) -> Channel:
        if self.type in (ChannelType.WEB, ChannelType.APP) and self.url is None:
            raise ValueError(f"a '{self.type}' channel needs a url")
        if self.type in (ChannelType.PHONE, ChannelType.TEXT) and self.phone is None:
            raise ValueError(f"a '{self.type}' channel needs a phone number")
        if self.type is ChannelType.EMAIL and self.email is None:
            raise ValueError("an 'email' channel needs an email address")
        return self


class Link(_Strict):
    label: str
    url: HttpUrl


class Steps(_Strict):
    """Numbered steps, written in plain language. Each list is one way of doing the task."""

    online: list[str] = Field(
        default_factory=list, description="Steps on a website (phone, tablet or computer)."
    )
    app: list[str] = Field(default_factory=list, description="Steps in a mobile app.")
    call: list[str] = Field(default_factory=list, description="Steps by telephone.")


class Overlap(_Strict):
    """Another jurisdiction this one overlaps, such as the counties a city lies in."""

    id: str = Field(description="Jurisdiction id (folder path), e.g. 'us/nc/county/wake'.")
    primary: bool = Field(default=False, description="True for the main/most common overlap.")
    notes: str | None = None


class Emergency(_Strict):
    """Emergency facts that vary by place. The emergency number itself is also hard-coded."""

    number: Text = Field(default="911", pattern=PHONE_PATTERN)
    text_to_911: bool | None = Field(
        default=None, description="Whether texting 911 works here. Null means unknown."
    )
    notes: str | None = None
    source_urls: list[HttpUrl] = Field(default_factory=list)


class Jurisdiction(_Strict):
    """A government (country, state, county, city/town, or special district)."""

    name: str = Field(description="Full name, e.g. 'City of Raleigh'.")
    kind: JurisdictionKind
    aliases: list[Text] = Field(
        default_factory=list, description="Short names accepted in lookups, e.g. 'raleigh'."
    )
    overlaps: list[Overlap] = Field(default_factory=list)
    websites: list[Link] = Field(default_factory=list)
    key_contacts: list[Channel] = Field(
        default_factory=list, description="The 'save these on your phone' list."
    )
    emergency: Emergency | None = None
    stewards: list[str] = Field(
        default_factory=list, description="GitHub handles of the volunteers who look after it."
    )
    notes: list[str] = Field(default_factory=list)
    provenance: Provenance


class Service(_Strict):
    """One thing a resident wants to get done, such as reporting a pothole."""

    id: str = Field(pattern=SLUG_PATTERN, description="Must match the file name, without .yaml.")
    title: str
    summary: str = Field(description="One or two plain-language sentences.")
    provider: str = Field(description="Who actually runs it, e.g. 'Raleigh Water'.")
    provider_type: ProviderType = ProviderType.GOVERNMENT
    category: Category
    core_skill: CoreSkill | None = None
    aliases: list[Text] = Field(
        default_factory=list, description="Words people might use: 'trash', 'garbage', 'bin'."
    )
    channels: list[Channel] = Field(min_length=1)
    what_you_need: list[str] = Field(default_factory=list)
    steps: Steps | None = None
    cost: str | None = None
    eligibility: str | None = None
    referral_only: bool = Field(
        default=False,
        description="True when we point people to it rather than teach it step by step.",
    )
    related: list[str] = Field(default_factory=list, description="Ids of related services.")
    notes: list[str] = Field(default_factory=list)
    provenance: Provenance


class RoutingRule(_Strict):
    """Maps a kind of situation to the right place to go."""

    id: str = Field(pattern=SLUG_PATTERN)
    situation: str = Field(description="Plain description, e.g. 'Question about a tax bill'.")
    keywords: list[Text] = Field(
        min_length=1, description="Words or phrases that suggest this situation."
    )
    go_to: str = Field(description="Who to contact, e.g. 'Wake County Tax Administration'.")
    jurisdiction: str | None = Field(
        default=None, description="Id of the jurisdiction that handles it."
    )
    service: str | None = Field(default=None, description="Id of a catalog service, if any.")
    channel: Channel | None = None
    explanation: str


class RoutingFallback(_Strict):
    go_to: str
    channel: Channel
    explanation: str


class Routing(_Strict):
    """The 'who do I contact?' table for one jurisdiction."""

    rules: list[RoutingRule] = Field(min_length=1)
    fallback: RoutingFallback
    provenance: Provenance


SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "jurisdiction": Jurisdiction,
    "service": Service,
    "routing": Routing,
}
"""File kind → model. ``civic-atlas schema`` writes ``schema/<kind>.schema.json`` for each."""
