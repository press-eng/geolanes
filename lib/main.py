from contextlib import asynccontextmanager

import strawberry
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from strawberry.fastapi import GraphQLRouter

from lib import config, scheduled_tasks, utils
from lib.graphql.types.mutation import Mutation
from lib.graphql.types.query import Query
from lib.helpers.campaign_helper import (
    check_and_publish_campaigns,
    check_and_unpublish_campaigns,
)
from lib.rest.routers import (
    campaign_router,
    customer_router,
    media_router,
    payment_router,
    social_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(config.MONGO_CONNSTR, authSource="admin")
    await init_beanie(
        database=client.get_default_database(),
        document_models=utils.get_beanie_models("lib.models"),
    )

    await scheduled_tasks.reset_auth_locks()
    await scheduled_tasks.send_confirm_tour_notifications()
    sched = AsyncIOScheduler()
    sched.add_job(scheduled_tasks.reset_auth_locks, "interval", hours=24)
    sched.add_job(scheduled_tasks.send_confirm_tour_notifications, "interval", hours=1)
    sched.add_job(check_and_publish_campaigns, "interval", hours=1)
    sched.add_job(check_and_unpublish_campaigns, "interval", hours=1)
    sched.start()

    yield
    sched.shutdown()


app = FastAPI(lifespan=lifespan, root_path=config.ROOT_PATH)
schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
)

app.include_router(graphql_app, prefix="/graphql")
app.include_router(media_router.router, prefix="/media")
app.include_router(social_router.router, prefix="/social")
app.include_router(payment_router.router, prefix="/payment")
app.include_router(campaign_router.router, prefix="/campaign")
app.include_router(customer_router.router, prefix="/customer")


@app.get("/")
def read_root():
    return {"Message": "Welcome to GL Backend!"}
