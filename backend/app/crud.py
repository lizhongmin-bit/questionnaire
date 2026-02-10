from typing import Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models, schemas
from .utils.security import generate_public_token


def create_survey(db: Session, payload: schemas.SurveyCreate) -> models.Survey:
    survey = models.Survey(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        link_template=payload.link_template,
    )
    for q in payload.questions:
        question = models.Question(
            title=q.title,
            description=q.description,
            required=q.required,
            sort_order=q.sort_order,
        )
        for opt in q.options:
            question.options.append(models.Option(text=opt.text, sort_order=opt.sort_order))
        survey.questions.append(question)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


def update_survey(db: Session, survey: models.Survey, payload: schemas.SurveyCreate) -> models.Survey:
    survey.title = payload.title
    survey.description = payload.description
    survey.status = payload.status
    survey.link_template = payload.link_template
    survey.questions.clear()
    for q in payload.questions:
        question = models.Question(
            title=q.title,
            description=q.description,
            required=q.required,
            sort_order=q.sort_order,
        )
        for opt in q.options:
            question.options.append(models.Option(text=opt.text, sort_order=opt.sort_order))
        survey.questions.append(question)
    db.commit()
    db.refresh(survey)
    return survey


def list_surveys(db: Session) -> List[models.Survey]:
    return list(db.scalars(select(models.Survey).order_by(models.Survey.created_at.desc())))


def get_survey(db: Session, survey_id: int) -> models.Survey | None:
    return db.get(models.Survey, survey_id)


def delete_survey(db: Session, survey: models.Survey) -> None:
    db.delete(survey)
    db.commit()


def get_survey_by_token(db: Session, token: str) -> models.Survey | None:
    stmt = (
        select(models.Survey)
        .join(models.DistributionToken, models.DistributionToken.survey_id == models.Survey.id)
        .where(models.DistributionToken.public_token == token)
    )
    return db.scalar(stmt)


def import_ids(db: Session, survey_id: int, ids: Iterable[str]) -> int:
    count = 0
    for real_id in ids:
        exists = db.scalar(
            select(func.count())
            .select_from(models.DistributionToken)
            .where(
                models.DistributionToken.survey_id == survey_id,
                models.DistributionToken.real_id == real_id,
            )
        )
        if exists:
            continue
        token = generate_public_token()
        while db.scalar(
            select(func.count())
            .select_from(models.DistributionToken)
            .where(
                models.DistributionToken.survey_id == survey_id,
                models.DistributionToken.public_token == token,
            )
        ):
            token = generate_public_token()
        db.add(
            models.DistributionToken(
                survey_id=survey_id,
                real_id=real_id,
                public_token=token,
            )
        )
        count += 1
    db.commit()
    return count


def list_tokens(db: Session, survey_id: int) -> List[models.DistributionToken]:
    stmt = select(models.DistributionToken).where(models.DistributionToken.survey_id == survey_id)
    return list(db.scalars(stmt))


def mark_submitted(db: Session, token: models.DistributionToken):
    token.submitted = True
    db.commit()


def create_submission(
    db: Session,
    survey: models.Survey,
    token: models.DistributionToken,
    answers: List[schemas.SubmitAnswer],
    ip: str | None,
    user_agent: str | None,
) -> models.Submission:
    submission = models.Submission(
        survey_id=survey.id,
        public_token=token.public_token,
        real_id=token.real_id,
        ip=ip,
        user_agent=user_agent,
    )
    option_map = {opt.id: opt for q in survey.questions for opt in q.options}
    for ans in answers:
        if not ans.option_id and not ans.option_text:
            continue
        option_text = None
        if ans.option_id:
            option = option_map.get(ans.option_id)
            if option:
                option_text = option.text
        if ans.option_text:
            option_text = ans.option_text
        submission.answers.append(
            models.Answer(
                question_id=ans.question_id,
                option_id=ans.option_id,
                option_text=option_text,
            )
        )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_submissions(db: Session, survey_id: int) -> List[models.Submission]:
    stmt = select(models.Submission).where(models.Submission.survey_id == survey_id).order_by(
        models.Submission.submitted_at.desc()
    )
    return list(db.scalars(stmt))


def build_stats(db: Session, survey: models.Survey):
    questions = []
    for question in sorted(survey.questions, key=lambda q: q.sort_order):
        total = db.scalar(
            select(func.count()).select_from(models.Answer).where(models.Answer.question_id == question.id)
        ) or 0
        options = []
        for opt in sorted(question.options, key=lambda o: o.sort_order):
            count = db.scalar(
                select(func.count())
                .select_from(models.Answer)
                .where(models.Answer.question_id == question.id, models.Answer.option_id == opt.id)
            ) or 0
            ratio = round(count / total, 4) if total else 0
            options.append((opt.id, opt.text, count, ratio))
        questions.append((question.id, question.title, total, options))
    return questions
