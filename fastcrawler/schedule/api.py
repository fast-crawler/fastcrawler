from fastapi import FastAPI
from rocketry.conditions.api import cron

from fastcrawler.schedule.app import app as app_rocketry

app = FastAPI()

# Import the Rocketry app
session = app_rocketry.session


@app.get("/scheduler/tasks/")
async def get_tasks():
    return session.tasks


@app.post("/scheduler/toggle/{task_name}")
async def toggle_task_enable(task_name: str):
    """
    Disables or enable one task
    """
    for task in session.tasks:
        if task.name == task_name:
            if task.disabled:
                task.disabled = False
            else:
                task.disabled = True


@app.post("/scheduler/reschedule/{task_name}")
async def reschedule_task(task_name: str, schedule_time: str):
    """
    Reschedule a task
        schedule:
            - can be string
                `every 2 seconds`
            - can be cron
                `*/2 * * * *`
    """
    for task in session.tasks:
        if task.name == task_name:
            if schedule_time.count(' ') == 4:
                task.start_cond = cron(schedule_time)
            else:
                task.start_cond = schedule_time
