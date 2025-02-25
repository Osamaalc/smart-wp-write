import os
from .BaseController import BaseController


class ProjectController(BaseController):
    def __init__(self):
        # Call the constructor of the base class (BaseController)
        super().__init__()

    def get_project_path(self, project_id: str):
        """
        Get the project path based on the project ID.
        If the path doesn't exist, it will be created.

        :param project_id: The ID of the project.
        :return: The path to the project directory.
        """
        project_dir = os.path.join(self.file_dir, project_id)

        # Create the directory if it doesn't exist
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir
