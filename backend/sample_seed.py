from app.db import SessionLocal
from app import crud, schemas


def main():
    db = SessionLocal()
    survey = crud.create_survey(
        db,
        schemas.SurveyCreate(
            title="用户满意度调查",
            description="用于测试的中文示例问卷",
            status="published",
            questions=[
                schemas.QuestionCreate(
                    title="您对本次服务的整体满意度？",
                    required=True,
                    sort_order=1,
                    options=[
                        schemas.OptionCreate(text="非常满意", sort_order=1),
                        schemas.OptionCreate(text="满意", sort_order=2),
                        schemas.OptionCreate(text="一般", sort_order=3),
                        schemas.OptionCreate(text="不满意", sort_order=4),
                    ],
                ),
                schemas.QuestionCreate(
                    title="您是否愿意再次选择我们？",
                    required=True,
                    sort_order=2,
                    options=[
                        schemas.OptionCreate(text="愿意", sort_order=1),
                        schemas.OptionCreate(text="不确定", sort_order=2),
                        schemas.OptionCreate(text="不愿意", sort_order=3),
                    ],
                ),
            ],
        ),
    )
    print("已创建示例问卷", survey.id)


if __name__ == "__main__":
    main()
