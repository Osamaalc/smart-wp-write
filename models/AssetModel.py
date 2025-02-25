from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        """
        Initialize the AssetModel with the provided database client.

        :param db_client: The database client used for interactions with the database.
        """
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create an instance of AssetModel and initialize its collection.

        :param db_client: The database client used for interactions with the database.
        :return: An instance of AssetModel.
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        """
        Initialize the collection for assets. Creates the collection and its indexes if it doesn't exist.

        :return: None
        """
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSETS_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index['key'], name=index['name'], unique=index['unique'])

    async def create_asset(self, asset: Asset):
        """
        Insert a new asset into the collection.

        :param asset: The asset to be created.
        :return: The created asset with an assigned ID.
        """
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset

    async def get_all_project_asset(self, asset_project_id: str, asset_type: str):
        """
        Retrieve all assets for a specific project and asset type.

        :param asset_project_id: The project ID associated with the assets.
        :param asset_type: The type of the assets.
        :return: A list of Asset objects.
        """
        result = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type,
        }).to_list(length=None)
        return [
            Asset(**record)
            for record in result
        ]

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        """
        Retrieve a specific asset record by project ID and asset name.

        :param asset_project_id: The project ID associated with the asset.
        :param asset_name: The name of the asset.
        :return: The Asset object if found, or None if not found.
        """
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,
        })
        if record:
            return Asset(**record)
        return None
