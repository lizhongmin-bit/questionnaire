from datetime import datetime
from io import BytesIO
from urllib.parse import quote
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import crud, models, schemas
from .db import Base, engine, settings
from .deps import get_db, require_admin
from .utils import excel
from .utils.dwz import shorten_url

app = FastAPI(title="定向调查问卷系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] ,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
    expose_headers=["Content-Disposition"],
)


@app.on_event("startup")
def on_startup():
    print(f"[CONFIG] export_links_format={settings.export_links_format}")
    Base.metadata.create_all(bind=engine)


@app.post("/api/admin/login", response_model=schemas.LoginOut)
def admin_login(payload: schemas.LoginPayload):
    if payload.username != settings.admin_user or payload.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    return {"token": settings.admin_token}


@app.get("/api/admin/surveys", response_model=list[schemas.SurveyListOut], dependencies=[Depends(require_admin)])
def admin_list_surveys(db: Session = Depends(get_db)):
    return crud.list_surveys(db)


@app.post("/api/admin/surveys", response_model=schemas.SurveyOut, dependencies=[Depends(require_admin)])
def admin_create_survey(payload: schemas.SurveyCreate, db: Session = Depends(get_db)):
    if payload.link_template and "${link}" not in payload.link_template:
        raise HTTPException(status_code=400, detail="链接模板必须包含 ${link}")
    return crud.create_survey(db, payload)


@app.get("/api/admin/surveys/{survey_id}", response_model=schemas.SurveyOut, dependencies=[Depends(require_admin)])
def admin_get_survey(survey_id: int, db: Session = Depends(get_db)):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    return survey


@app.put("/api/admin/surveys/{survey_id}", response_model=schemas.SurveyOut, dependencies=[Depends(require_admin)])
def admin_update_survey(survey_id: int, payload: schemas.SurveyCreate, db: Session = Depends(get_db)):
    if payload.link_template and "${link}" not in payload.link_template:
        raise HTTPException(status_code=400, detail="链接模板必须包含 ${link}")
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    return crud.update_survey(db, survey, payload)


@app.delete("/api/admin/surveys/{survey_id}", dependencies=[Depends(require_admin)])
def admin_delete_survey(survey_id: int, db: Session = Depends(get_db)):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    crud.delete_survey(db, survey)
    return {"deleted": True}


@app.post("/api/admin/surveys/{survey_id}/import-ids", dependencies=[Depends(require_admin)])
def admin_import_ids(
    survey_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    content = file.file.read()
    ids, errors = excel.parse_id_xlsx(content, expected_header="ID")
    if errors:
        raise HTTPException(status_code=400, detail=";".join(errors))
    count = crud.import_ids(db, survey_id, ids)
    return {"imported": count, "total": len(ids)}


@app.get("/api/admin/id-template", dependencies=[Depends(require_admin)])
def admin_download_template():
    data = excel.build_id_template("ID")
    filename = "ID导入模板.xlsx"
    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": disposition},
    )


@app.get("/api/admin/surveys/{survey_id}/export-links", dependencies=[Depends(require_admin)])
def admin_export_links(
    survey_id: int,
    public_base_url: str | None = None,
    db: Session = Depends(get_db),
):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    tokens = crud.list_tokens(db, survey_id)
    base_url = public_base_url or settings.public_base_url
    if not base_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="public_base_url 必须以 http:// 或 https:// 开头")
    if not settings.dwz_token:
        raise HTTPException(status_code=500, detail="未配置 DWZ_TOKEN")
    if not survey.link_template or "${link}" not in survey.link_template:
        raise HTTPException(status_code=400, detail="请在问卷配置中设置包含 ${link} 的链接模板")
    rows = []
    for token in tokens:
        link = f"{base_url}/s/{token.public_token}"
        try:
            short_url = shorten_url(
                link,
                settings.dwz_token,
                settings.dwz_term,
                settings.dwz_api_base,
                settings.dwz_ssl_verify,
                settings.dwz_ca_file,
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"短网址生成失败: {exc}") from exc
        content = survey.link_template.replace("${link}", short_url)
        rows.append((token.real_id, content))
    export_format = settings.export_links_format.lower().strip()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_title = (survey.title or "问卷").replace("/", "-").replace("\\", "-")
    if export_format == "txt":
        data = excel.build_links_txt(rows)
        filename = f"{safe_title}_{timestamp}.txt"
        media_type = "text/plain; charset=utf-8"
    else:
        data = excel.build_links_xlsx(rows)
        filename = f"{safe_title}_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return StreamingResponse(
        BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": disposition},
    )


@app.get("/api/s/{token}", response_model=schemas.PublicSurveyOut)
def public_get_survey(token: str, db: Session = Depends(get_db)):
    token_model = db.scalar(
        select(models.DistributionToken).where(models.DistributionToken.public_token == token)
    )
    if not token_model:
        raise HTTPException(status_code=404, detail="链接无效")
    survey = crud.get_survey(db, token_model.survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    submitted = bool(token_model.submitted and not settings.allow_resubmit)
    response = schemas.PublicSurveyOut.model_validate(survey, from_attributes=True)
    response.submitted = submitted
    return response


@app.post("/api/s/{token}/submit")
def public_submit(token: str, payload: schemas.SubmitPayload, db: Session = Depends(get_db)):
    token_model = db.scalar(
        select(models.DistributionToken).where(models.DistributionToken.public_token == token)
    )
    if not token_model:
        raise HTTPException(status_code=404, detail="链接无效")
    if token_model.submitted and not settings.allow_resubmit:
        raise HTTPException(status_code=400, detail="该链接已提交")
    survey = crud.get_survey(db, token_model.survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    answer_map = {ans.question_id: ans for ans in payload.answers}
    for question in survey.questions:
        if question.required and question.id not in answer_map:
            raise HTTPException(status_code=400, detail="有必答题未填写")
        ans = answer_map.get(question.id)
        if ans and ans.option_id:
            valid_ids = {opt.id for opt in question.options}
            if ans.option_id not in valid_ids:
                raise HTTPException(status_code=400, detail="选项不合法")
    submission = crud.create_submission(
        db,
        survey,
        token_model,
        payload.answers,
        None,
        None,
    )
    crud.mark_submitted(db, token_model)
    return {"submission_id": submission.id, "submitted_at": submission.submitted_at}


@app.get("/api/admin/surveys/{survey_id}/submissions", response_model=list[schemas.SubmissionOut], dependencies=[Depends(require_admin)])
def admin_list_submissions(survey_id: int, db: Session = Depends(get_db)):
    return crud.list_submissions(db, survey_id)


@app.get("/api/admin/surveys/{survey_id}/stats", response_model=schemas.StatsOut, dependencies=[Depends(require_admin)])
def admin_stats(survey_id: int, db: Session = Depends(get_db)):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    stats = crud.build_stats(db, survey)
    questions = []
    for q_id, title, total, options in stats:
        questions.append(
            schemas.StatsQuestion(
                question_id=q_id,
                title=title,
                total=total,
                options=[
                    schemas.StatsOption(option_id=o_id, text=text, count=count, ratio=ratio)
                    for o_id, text, count, ratio in options
                ],
            )
        )
    return schemas.StatsOut(survey_id=survey_id, questions=questions)


@app.get("/api/admin/surveys/{survey_id}/export-answers", dependencies=[Depends(require_admin)])
def admin_export_answers(survey_id: int, db: Session = Depends(get_db)):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="问卷不存在")
    submissions = crud.list_submissions(db, survey_id)
    questions = sorted(survey.questions, key=lambda q: q.sort_order)
    option_order_map = {}
    for q in questions:
        sorted_opts = sorted(q.options, key=lambda o: o.sort_order)
        option_order_map[q.id] = {opt.id: str(idx + 1) for idx, opt in enumerate(sorted_opts)}
    headers = ["ID", "提交时间"] + [f"第{idx + 1}题" for idx, _ in enumerate(questions)]
    rows = []
    for sub in submissions:
        answer_map = {ans.question_id: ans for ans in sub.answers}
        row = [sub.real_id, sub.submitted_at.strftime("%Y-%m-%d %H:%M:%S")]
        for q in questions:
            ans = answer_map.get(q.id)
            if not ans or not ans.option_id:
                row.append("")
            else:
                row.append(option_order_map.get(q.id, {}).get(ans.option_id, ""))
        rows.append(row)
    data = excel.build_answers_xlsx(headers, rows)
    filename = "答案导出.xlsx"
    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": disposition},
    )
