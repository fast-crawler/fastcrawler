from datetime import datetime

from rocketry import Rocketry
from rocketry.args import Config, EnvArg
from rocketry.conditions.api import cron

from .schema import ConfigDataClass

app = Rocketry(execution="async")


@app.setup()
def set_config(
    config: ConfigDataClass = Config(),
    env=EnvArg("ENV", default="dev")
):
    if env == "prod":
        config.silence_task_prerun = True
        config.silence_task_logging = True
        config.silence_cond_check = True
    else:
        config.silence_task_prerun = False
        config.silence_task_logging = False
        config.silence_cond_check = False


@app.task(cron('* * * * *'))
def hello():
    print("Hello", datetime.now())
