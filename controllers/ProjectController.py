import os

from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal


class ProjectController(BaseController):
    def __init__(self):
        # استدعاء دالة البناء من الكلاس الأساسي (BaseController)
        super().__init__()

    def get_project_path(self, project_id: str):
        """
        الحصول على مسار المشروع بناءً على معرف المشروع.
        إذا لم يكن المسار موجودًا، يتم إنشاؤه.
        """
        project_dir = os.path.join(self.file_dir, project_id)

        # إنشاء المسار إذا لم يكن موجودًا
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir