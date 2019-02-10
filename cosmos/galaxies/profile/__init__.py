from .profile import Profile
from .economy import Economy
from .ascension import Levels
from .marriage import Marriage

from .models import ProfileCache

__all__ = [
    Profile,
    Levels,
    Economy,
    Marriage
]


def setup(bot):
    # plugin = bot.plugins.setup(__file__, cache=ProfileCache)    # setup method automatically passes plugin.
    plugin = bot.plugins.get_from_file(__file__)
    plugin.collection = bot.db[plugin.data.profile.collection_name]
    plugin.batch = bot.db_client.batch(bot, plugin.collection)
    plugin.cache = ProfileCache(plugin)

    plugin.load_cogs(__all__)
