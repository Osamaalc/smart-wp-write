import logging
import os

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse

from controllers import DataController, ProjectController, ProcessController
from helpers.config import get_settings, Settings
from models import ResponseSignal
from models.db_schemes import Project
from routes.schems.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk, Asset
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum


# Setup logger for error logging
logger = logging.getLogger('uvicorn.error')

# Create router for data endpoints
data_router = APIRouter(
    prefix="/api/v1/data",  # Prefix for the route
    tags=["api_v1", "data"]  # Tag for documentation
)


@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    """
    Endpoint for uploading files to a specific project directory.
    """
    # Create an instance of DataController to validate the uploaded file
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    # If the file is invalid, return an error message
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal}  # Use dictionary for signal
        )

    # Get the project directory path
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    # Generate a unique file name
    file_path, file_id = data_controller.generate_unique_filepath(orig_file_name=file.filename, project_id=project_id)

    try:
        # Upload the file to the specified path
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        # Log the error if the upload fails
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )

    # Store the asset into the dataset
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )
    asset_record = await asset_model.create_asset(asset=asset_resource)

    # Return success message if the upload was successful
    return JSONResponse(
        content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                 "file_id": str(asset_record.id),
                 }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    """
    Endpoint to process files and break them into chunks for a specific project.
    """
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_rest

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=process_request.file_id)
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value
                }
            )
        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }

    else:
        project_file = await asset_model.get_all_project_asset(asset_project_id=project.id,
                                                               asset_type=AssetTypeEnum.FILE.value)
        project_files_ids = {
            record.id: record.asset_name
            for record in project_file
        }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value
            }
        )

    process_controller = ProcessController(project_id=project_id)
    no_records = 0
    no_file = 0
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    for asset_id, file_id in project_files_ids.items():
        file_content = await process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = await process_controller.process_file_content(file_content=file_content, file_id=file_id,
                                                                   chunk_size=chunk_size, overlap_size=overlap_size)
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROCESSING_FAILED.value}
            )

        # Create the list of chunks
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,  # Ensure chunk_size is defined
                chunk_order=i + 1,
                chunk_project_id=project.id,  # Ensure Project and Project._id are defined
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_file += 1

    return JSONResponse(
        content={"signal": ResponseSignal.PROCESSING_SUCCESS.value,
                 "inserted_records": no_records,
                 "processed_files": no_file, }
    )
