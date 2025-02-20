# # 1. تعريف نموذج الطلب الموحد
#
# # يجب أن يحتوي ملفك على هذه الاستيرادات:
# from fastapi import APIRouter, Depends, UploadFile, status, Request
# from pydantic import BaseModel
# from openai import BaseModel
# from fastapi.responses import JSONResponse
#
# from controllers import ProjectController, NLPController
# from helpers.config import Settings, get_settings
# from models.ChunkModel import ChunkModel
# from models.ProjectModel import ProjectModel
# from routes.data import data_router, upload_data, process_endpoint, logger
# from routes.nlp import index_project
# from routes.schems.data import ProcessRequest
# from routes.schems.nlp import PushRequest
#
#
# class UnifiedProcessRequest(BaseModel):
#     file: UploadFile
#     chunk_size: int
#     overlap_size: int
#     do_reset_processing: int = 0
#     do_reset_index: int = 0
# file_router=APIRouter(
#     prefix="/api/v1/nlp",
#     tags=["api_v1","nlp"]
# )
#
# # 2. إنشاء نقطة النهاية الجديدة
# @data_router.post("/unified-process/{project_id}")
# async def unified_process(
#         request: Request,
#         project_id: str,
#         unified_request: UnifiedProcessRequest,
#         app_settings: Settings = Depends(get_settings)
# ):
#     try:
#         # التحقق من وجود المشروع أولًا
#         project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
#         project = await project_model.get_project_or_create_one(project_id=project_id)
#
#         if not project:
#             return JSONResponse(
#                 status_code=404,
#                 content={"signal": "PROJECT_NOT_FOUND"}
#             )
#
#         # ===== 1. مرحلة التحميل =====
#         upload_result = await upload_data(
#             request=request,
#             project_id=project_id,
#             file=unified_request.file,
#             app_settings=app_settings
#         )
#
#         if upload_result.status_code != 200:
#             raise ValueError("File upload failed")
#
#         uploaded_file_id = upload_result.body['file_id']
#
#         # ===== 2. مرحلة المعالجة =====
#         process_result = await process_endpoint(
#             request=request,
#             project_id=project_id,
#             process_request=ProcessRequest(
#                 chunk_size=unified_request.chunk_size,
#                 overlap_size=unified_request.overlap_size,
#                 do_rest=unified_request.do_reset_processing,
#                 file_id=uploaded_file_id
#             )
#         )
#
#         if process_result.status_code != 200:
#             raise ValueError("Data processing failed")
#
#         # ===== 3. مرحلة الفهرسة =====
#         index_result = await index_project(
#             request=request,
#             project_id=project_id,
#             push_request=PushRequest(
#                 do_rest=unified_request.do_reset_index
#             )
#         )
#
#         if index_result.status_code != 200:
#             raise ValueError("Indexing failed")
#
#         # ===== النتيجة النهائية =====
#         return JSONResponse(
#             status_code=200,
#             content={
#                 "signal": "FULL_PROCESS_SUCCESS",
#                 "details": {
#                     "uploaded_file": uploaded_file_id,
#                     "processed_chunks": process_result.body['inserted_records'],
#                     "indexed_items": index_result.body['inserted_items_count']
#                 }
#             }
#         )
#
#     except Exception as e:
#         # التراجع عن التغييرات عند الخطأ
#         # await cleanup_resources(project_id)
#
#         logger.error(f"Unified process failed: {str(e)}")
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "signal": "FULL_PROCESS_FAILED",
#                 "error": str(e)
#             }
#         )
#
#
# # # دالة مساعدة للتنظيف
# # async def cleanup_resources(project_id: str):
# #     try:
# #         # حذف الملفات المؤقتة
# #         ProjectController().delete_project_files(project_id)
# #
# #         # حذف السجلات من قاعدة البيانات
# #         chunk_model = await ChunkModel.create_instance(...)
# #         await chunk_model.delete_chunks_by_project_id(project_id)
# #
# #         # حذف الفهرسة
# #         nlp_controller = NLPController(...)
# #         nlp_controller.delete_project_index(project_id)
# #
# #     except Exception as e:
# #         logger.error(f"Cleanup error: {str(e)}")