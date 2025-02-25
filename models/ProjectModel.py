from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        """
        Initialize the ProjectModel with the provided database client.

        :param db_client: The database client used for interactions with the database.
        """
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Create an instance of ProjectModel and initialize its collection.

        :param db_client: The database client used for interactions with the database.
        :return: An instance of ProjectModel.
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        """
        Initialize the collection for projects. Creates the collection and its indexes if not already present.

        :return: None
        """
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index['key'], name=index['name'], unique=index['unique'])

    async def create_project(self, project: Project):
        """
        Insert a new project into the collection.

        :param project: The project to be created.
        :return: The created project with an assigned ID.
        """
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        """
        Retrieve a project by its project ID, or create a new project if not found.

        :param project_id: The project ID to retrieve or create.
        :return: The found or newly created project.
        """
        record = await self.collection.find_one({"project_id": project_id})
        if record is None:
            # Create a new project if not found
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            return project

        return Project(**record)

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        """
        Retrieve all projects with pagination.

        :param page: The page number to retrieve. Default is 1.
        :param page_size: The number of projects per page. Default is 10.
        :return: A tuple containing a list of projects and the total number of pages.
        """
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))

        return projects, total_pages
