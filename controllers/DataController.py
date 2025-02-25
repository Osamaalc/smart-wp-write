import os
import re

from fastapi import UploadFile
from models import ResponseSignal
from .BaseController import BaseController
from .ProjectController import ProjectController


class DataController(BaseController):
    def __init__(self):
        # Call the constructor of the base class (BaseController)
        super().__init__()
        # Define file size limit in bytes (1 MB = 1048576 bytes)
        self.size_scale = 1048576

    def validate_uploaded_file(self, file: UploadFile):
        """
        Validate the uploaded file.

        :param file: The uploaded file to validate.
        :return: Tuple (Boolean indicating validity, validation message)
        """
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_TOO_LARGE.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        """
        Generate a unique file path based on the original file name and project ID.

        :param orig_file_name: The original file name.
        :param project_id: The project ID to create a project-specific file path.
        :return: The unique file path and the new file name.
        """
        random_key = self.genarate_random_string()
        project_controller = ProjectController()
        project_path = project_controller.get_project_path(project_id=project_id)
        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        # Ensure the file name is unique
        while os.path.exists(new_file_path):
            random_key = self.genarate_random_string()
            new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        """
        Clean the file name by removing unwanted characters.

        :param orig_file_name: The original file name to clean.
        :return: The cleaned file name.
        """
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(' ', '_')
        return cleaned_file_name
