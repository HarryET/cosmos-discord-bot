import arrow

from .currency import Boson, Fermion
from .experience import UserExperience
from .family import Relationship

from ..guild import GuildMemberProfile


class CosmosUserProfile(UserExperience, Boson, Fermion, Relationship):

    @property
    def plugin(self):
        return self.__plugin

    @property
    def collection(self):
        return self.__collection

    @property
    def id(self):
        return self._id

    @property
    def is_prime(self):
        return self._is_prime

    @property
    def description(self):
        return self._description or self.plugin.data.profile.default_description

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    def __init__(self, plugin, **kwargs):
        UserExperience.__init__(self, **kwargs)
        Boson.__init__(self, **kwargs)
        Fermion.__init__(self, **kwargs)
        Relationship.__init__(self, **kwargs)
        self.__plugin = plugin
        self._id: int = kwargs["user_id"]
        self._is_prime = kwargs.get("is_prime", False)
        raw_reputation = kwargs.get("reputation", dict())
        self.reps: int = raw_reputation.get("points", 0)
        self.rep_timestamp = self.get_arrow(raw_reputation.get("timestamp"))
        # self.badges = []
        self._description: str = kwargs.get("description", str())
        self.birthday = self.get_arrow(kwargs.get("birthday"))
        self.rank: int = None
        # self.inventory = []
        # self.on_time: int = None
        self.guild_profiles = self.plugin.bot.cache.lfu(self.plugin.data.profile.guild_profiles_cache_max_size)
        self.__collection = self.plugin.collection
        if self.plugin.data.profile.fetch_guild_profiles:
            self.plugin.bot.create_task(self.__fetch_guild_profiles())    # TODO: Fetch profiles of all guilds.

    @property
    def can_rep(self):
        if not self.rep_timestamp:    # Using rep for first time.
            return True
        return arrow.utcnow() > self.next_rep

    @property
    def next_rep(self):
        return self.get_future_arrow(self.rep_timestamp, hours=self.plugin.data.profile.rep_cooldown)

    async def rep(self, author_profile):
        self.reps += 1
        author_profile.rep_timestamp = arrow.utcnow()
        await self.collection.update_one(
            self.document_filter, {"$set": {"reputation.points": self.reps}}
        )
        await self.collection.update_one(
            author_profile.document_filter, {"$set": {"reputation.timestamp": author_profile.rep_timestamp.datetime}}
        )

    async def set_description(self, description: str):
        self._description = description
        await self.collection.update_one(
            self.document_filter, {"$set": {"description": self.description}}
        )

    async def set_birthday(self, birthday):
        if isinstance(birthday, str):
            birthday = arrow.get(birthday)
        self.birthday = birthday

        await self.collection.update_one(
            self.document_filter, {"$set": {"birthday": birthday.datetime}}
        )

    def to_update_document(self) -> tuple:
        update = {
            "$set": {
                "xp": self.xp,
                "level": self.level,
                "currency.bosons": self.bosons
            }
        }
        return self.document_filter, update

    def get_embed(self):
        embed = self.plugin.bot.theme.embeds.primary(title="Cosmos Profile")
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name="Level", value=self.level)
        embed.add_field(name="Experience points", value=self.xp)
        embed.add_field(name="Delta Experience points", value=self.delta_xp)
        embed.add_field(name="Reputation points", value=self.reps)
        embed.add_field(name="Prime", value=self.is_prime)
        embed.add_field(name="Bosons", value=self.bosons)
        embed.add_field(name="Fermions", value=self.fermions)
        embed.add_field(name="Rank", value=self.rank)
        embed.add_field(name="💖  Proposed", value=self.proposed)
        embed.add_field(name="🖤  Proposer", value=self.proposer)
        if self.spouse_id:
            embed.add_field(name="💍  Spouse", value=f"{self.spouse}\nMarried {self.marriage_timestamp.humanize()}.")
        if self.birthday:
            embed.add_field(name="Birthday", value=self.birthday.strftime("%e %B"))
        embed.add_field(name="Parents", value=self.parents)
        embed.add_field(name="Family", value=self.children)
        embed.add_field(name="Profile description", value=self.description)
        return embed

    async def __fetch_guild_profiles(self):
        pass

    async def get_guild_profile(self, guild_id: int) -> GuildMemberProfile:
        profile = self.guild_profiles.get(guild_id)
        if not profile:
            document = await self.collection.find_one(
                self.document_filter, {f"guilds.{guild_id}": "$"}
            ) or dict()
            document = document.get("guilds", dict())
            profile = GuildMemberProfile.from_document(self, guild_id, document)
            self.guild_profiles.set(guild_id, profile)
        return profile