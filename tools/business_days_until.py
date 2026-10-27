from datetime import date, timedelta
from typing import ClassVar, Optional

from pydantic import BaseModel, Field, model_validator
from trase_os_sdk.tools import BaseTool

MAX_SPAN_DAYS = 3660  # about 10 years; keeps a bad input from looping forever


class BusinessDaysInput(BaseModel):
    due_date: date = Field(
        description="The deadline, in ISO format YYYY-MM-DD.",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Count from this date, YYYY-MM-DD. Omit to count from today.",
    )
    holidays: list[date] = Field(
        default_factory=list,
        max_length=100,
        description="Non-working weekdays to skip, each YYYY-MM-DD. Optional.",
    )

    @model_validator(mode="after")
    def check_span(self):
        start = self.start_date or date.today()
        if abs((self.due_date - start).days) > MAX_SPAN_DAYS:
            raise ValueError(
                f"due_date must be within {MAX_SPAN_DAYS} days of start_date"
            )
        return self


class BusinessDaysUntil(BaseTool):
    name: ClassVar[str] = "UatBusinessDaysUntil"
    description: ClassVar[str] = (
        "Count working days (Monday to Friday, minus any holidays) from a start "
        "date to a due date. Negative when the due date has already passed."
    )
    pydantic_inputs: ClassVar[type[BaseModel]] = BusinessDaysInput
    output_type: ClassVar[str] = "object"

    def forward(
        self,
        due_date: str,
        start_date: Optional[str] = None,
        holidays: Optional[list[str]] = None,
    ) -> dict:
        inputs = BusinessDaysInput(
            due_date=due_date,
            start_date=start_date,
            holidays=holidays or [],
        )
        start = inputs.start_date or date.today()
        due = inputs.due_date
        skip = set(inputs.holidays)

        # Count the days after start, up to and including due.
        # If due is in the past, count backwards and make the result negative.
        step = 1 if due >= start else -1
        business_days = 0
        day = start
        while day != due:
            day += timedelta(days=step)
            if day.weekday() < 5 and day not in skip:
                business_days += step

        return {
            "start_date": start.isoformat(),
            "due_date": due.isoformat(),
            "business_days": business_days,
            "calendar_days": (due - start).days,
            "holidays_skipped": sorted(
                h.isoformat()
                for h in skip
                if h.weekday() < 5 and min(start, due) < h <= max(start, due)
            ),
            "is_overdue": due < start,
        }
