import os
import re

from fastapi import UploadFile

from models import ResponseSignal
from .BaseController import BaseController
from .ProjectController import ProjectController


class DataController(BaseController):
    def __init__(self):
        # استدعاء دالة البناء من الكلاس الأساسي (BaseController)
        super().__init__()
        # تعريف حجم الملف بالميجابايت (1 ميجابايت = 1048576 بايت)
        self.size_scale = 1048576

    def validate_uploaded_file(self, file: UploadFile):
        """
        التحقق من صحة الملف المرفوع.
        """
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_TOO_LARGE.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        """
        إنشاء اسم ملف فريد بناءً على اسم الملف الأصلي ومعرف المشروع.
        """
        random_key = self.genarate_random_string()
        project_controller = ProjectController()
        project_path = project_controller.get_project_path(project_id=project_id)
        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        # التأكد من أن اسم الملف فريد
        while os.path.exists(new_file_path):
            random_key = self.genarate_random_string()
            new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        return new_file_path,random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        """
        تنظيف اسم الملف من الأحرف غير المرغوب فيها.
        """
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(' ', '_')
        return cleaned_file_name