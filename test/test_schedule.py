import asyncio

import pytest

from fastcrawler.schedule.adopter import RocketryApplication, RocketryManager, TaskNotFound
from fastcrawler.schedule.schema import Task


@pytest.fixture(scope="function")
def app():
    yield RocketryApplication()


@pytest.fixture(scope="function")
def manager(app):
    yield RocketryManager(app)


async def task_function(sleep_sec=5):
    print(f"going to sleep for {sleep_sec} seconds")
    await asyncio.sleep(sleep_sec)


sample_tasks = [
    Task(
        name="tast_1",
        description="Task 1 Description",
        logger_name="test_task_1",
    ),
    Task(
        name="tast_2",
        description="Task 2 Description",
        logger_name="test_task_2",
    ),
]


def get_task(num=1):
    return sample_tasks[num - 1]


@pytest.mark.asyncio
async def test_add_task_to_rocketry_application(app: RocketryApplication):
    new_task_1 = get_task(1)
    task_names = {task.name for task in (new_task_1,)}
    await app.add_task(task_function, new_task_1)
    session_tasks = app.task_lib.session.tasks
    session_task_names = {session_task.name for session_task in session_tasks}
    assert session_task_names == task_names, "The task not added correctly!"


@pytest.mark.asyncio
async def test_get_all_task_to_rocketry_application(app: RocketryApplication):
    new_task_1 = get_task(1)
    new_task_2 = get_task(2)
    task_names = {task.name for task in (new_task_1, new_task_2)}
    await app.add_task(task_function, new_task_1)
    await app.add_task(task_function, new_task_2)
    session_tasks = await app.get_all_tasks()
    session_task_names = {session_task.name for session_task in session_tasks}
    assert session_task_names == task_names, "The task not added correctly!"


@pytest.mark.asyncio
async def test_shutdown_rocketry_application(app: RocketryApplication):
    new_task_1 = get_task(1)
    await app.add_task(task_function, new_task_1)
    await asyncio.sleep(1)
    await app.shut_down()
    await asyncio.sleep(1)
    assert not app.task_lib.session.scheduler.is_alive


# @pytest.mark.asyncio
# async def test_serve_rocketry_application(app: RocketryApplication):
#     new_task_1 = get_task(1)
#     await app.add_task(task_function, new_task_1)
#     await asyncio.sleep(1)
#     await app.serve()
#     await asyncio.sleep(1)
#     assert app.task_lib.session.scheduler.is_alive


@pytest.mark.asyncio
async def test_add_task_to_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    session_tasks = await manager.app.get_all_tasks()
    session_task_names = {session_task.name for session_task in session_tasks}
    assert session_task_names == task_names, "The task not added correctly!"


@pytest.mark.asyncio
async def test_all_tasks_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    new_task_2 = get_task(2)
    task_names = {task.name for task in (new_task_1, new_task_2)}
    await manager.add_task(task_function, new_task_1)
    await manager.add_task(task_function, new_task_2)
    session_tasks = await manager.all()
    session_task_names = {session_task.name for session_task in session_tasks}
    assert session_task_names == task_names, "The task not added correctly!"


@pytest.mark.asyncio
async def test_change_task_schedule_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    # if any problem is encountered during change_task_schedule it should raise an exception
    await manager.change_task_schedule(new_task_1.name, "*/2 * * * *")
    assert True


@pytest.mark.asyncio
async def test_change_task_schedule_string_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    # if any problem is encountered during change_task_schedule it should raise an exception
    await manager.change_task_schedule(new_task_1.name, "every 2 seconds")
    assert True


@pytest.mark.xfail(raises=TaskNotFound)
@pytest.mark.asyncio
async def test_fail_test_change_task_schedule_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    await manager.add_task(task_function, new_task_1)
    await manager.change_task_schedule("wrong_task_name", "every 2 seconds")


@pytest.mark.asyncio
async def test_toggle_task_not_disabled_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    # if any problem is encountered during toggle_task it should raise an exception
    await manager.toggle_task(new_task_1.name)
    assert True


@pytest.mark.asyncio
async def test_toggle_task_disabled_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    new_task_1.disabled = True
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    # if any problem is encountered during toggle_task it should raise an exception
    await manager.toggle_task(new_task_1.name)
    assert True


@pytest.mark.xfail(raises=TaskNotFound)
@pytest.mark.asyncio
async def test_toggle_task_not_found_from_manager(manager: RocketryManager):
    new_task_1 = get_task(1)
    task_names = {new_task_1.name}
    await manager.add_task(task_function, new_task_1)
    # if any problem is encountered during toggle_task it should raise an exception
    await manager.toggle_task("wromg_task_name")
    assert True
