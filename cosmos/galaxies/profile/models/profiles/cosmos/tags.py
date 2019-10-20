from abc import ABC

from ..base import ProfileModelsBase


class Tag(object):

    def __init__(self, name, content):
        self.name = name
        self.content = content

    @property
    def document(self):
        return {
            "name": self.name,
            "content": self.content
        }


class UserTags(ProfileModelsBase, ABC):

    def __init__(self, documents):
        self.tags = [Tag(_["name"], _["content"]) for _ in documents]

    def __bool__(self):
        return bool(self.tags)

    def get_tag(self, name):
        try:
            return [tag for tag in self.tags if tag.name.lower() == name][0]
        except IndexError:
            pass

    def __remove_tag(self, name):
        tag = self.get_tag(name)
        self.tags.remove(tag)

    async def create_tag(self, name, content):
        if self.get_tag(name):
            self.__remove_tag(name)    # Replace tag with new content.
        tag = Tag(name, content)
        self.tags.append(tag)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"tags": {"name": {"$or": [tag.name, tag.name.lower()]}}}}
        )    # Pull if already exists.
        await self.collection.update_one(
            self.document_filter, {"$addToSet": {"tags": tag.document}}
        )

    async def remove_tag(self, name):
        self.__remove_tag(name)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"tags": {"name": {"$or": [name, name.lower()]}}}}
        )