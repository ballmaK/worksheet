from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.work_log_template import WorkLogTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse
from app.schemas.work_log import WorkLogCreate

router = APIRouter()

@router.post("", response_model=TemplateResponse)
def create_template(
    *,
    db: Session = Depends(get_db),
    template_in: TemplateCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建工作日志模板
    """
    # 如果设置为默认模板，先取消其他默认模板
    if template_in.is_default:
        db.query(WorkLogTemplate).filter(
            WorkLogTemplate.user_id == current_user.id,
            WorkLogTemplate.is_default == True
        ).update({"is_default": False})
    
    template = WorkLogTemplate(
        user_id=current_user.id,
        **template_in.dict()
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("", response_model=List[TemplateResponse])
def read_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    work_type: Optional[str] = None,
) -> Any:
    """
    获取工作日志模板列表
    """
    query = db.query(WorkLogTemplate).filter(WorkLogTemplate.user_id == current_user.id)
    if work_type:
        query = query.filter(WorkLogTemplate.work_type == work_type)
    templates = query.order_by(WorkLogTemplate.use_count.desc()).all()
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
def read_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定模板
    """
    template = db.query(WorkLogTemplate).filter(
        WorkLogTemplate.id == template_id,
        WorkLogTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    template_in: TemplateUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新模板
    """
    template = db.query(WorkLogTemplate).filter(
        WorkLogTemplate.id == template_id,
        WorkLogTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    # 如果设置为默认模板，先取消其他默认模板
    if template_in.is_default:
        db.query(WorkLogTemplate).filter(
            WorkLogTemplate.user_id == current_user.id,
            WorkLogTemplate.is_default == True,
            WorkLogTemplate.id != template_id
        ).update({"is_default": False})
    
    for field, value in template_in.dict(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}")
def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除模板
    """
    template = db.query(WorkLogTemplate).filter(
        WorkLogTemplate.id == template_id,
        WorkLogTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    db.delete(template)
    db.commit()
    return {"status": "success"}

@router.post("/{template_id}/use", response_model=WorkLogCreate)
def use_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    使用模板创建工作日志
    """
    template = db.query(WorkLogTemplate).filter(
        WorkLogTemplate.id == template_id,
        WorkLogTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    # 更新使用次数
    template.use_count += 1
    db.add(template)
    db.commit()
    
    # 返回预填充的工作日志数据
    return WorkLogCreate(
        work_type=template.work_type,
        content=template.content_template,
        duration=template.duration or 0.0,
        tags=template.tags
    ) 