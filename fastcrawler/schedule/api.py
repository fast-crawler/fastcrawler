# Create FastAPI app
from fastapi import FastAPI

app = FastAPI()

# Import the Rocketry app
from fastcrawler.schedule.app import app as app_rocketry
session = app_rocketry.session

@app.get("/scheduler/tasks/")
async def get_tasks():
    return session.tasks

@app.post("/scheduler/toggle/{task_name}")
async def toggle_task_enable(task_name:str):
    """
    disable or enable one task
    """
    for task in session.tasks:
        if task.name==task_name:
            if task.disabled:
                task.disabled = False
            else:
                task.disabled = True


@app.post("/scheduler/reschedule/{task_name}")
async def reschedule_task(task_name:str,schedule_time:str):
    """
    reschedule a task
    schedule:
        - could be string 
            every 2 seconds
        - could be cron
            */2 * * * *

    """
    for task in session.tasks:
        if task.name==task_name:
            if schedule_time.count(' ') == 4:
                from rocketry.conditions.api import cron
                task.start_cond = cron(schedule_time)
            else:
                task.start_cond = schedule_time
