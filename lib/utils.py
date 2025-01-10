import importlib
import inspect
import pkgutil
import re
from typing import List

from beanie import Document, PydanticObjectId
from strawberry.types import Info

from lib.graphql.types.error import Error
from lib.helpers.customer_helper import get_verified_customer



def validate_then_handle(config, input):
    fields = [k for k, v in input.__dict__.items() if bool(v)]
    conf = next((c for c in config if set(c["args"]) == set(fields)), None)
    if conf:
        return conf["handler"](input)

    combinations = [f"({', '.join(c['args'])})" for c in config]
    raise ValueError(f"Invalid input combination! Try: {', '.join(combinations)}.")


def is_valid_email(email):
    return bool(re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}$", email))


def get_beanie_models(package_name):
    path = "/".join(package_name.split("."))
    modules = [
        module_name for _, module_name, _ in pkgutil.iter_modules([path], prefix=f"{package_name}.")
    ]

    classes = []
    for module_name in modules:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Document) and not obj == Document:
                classes.append(obj)

    return classes


async def create_delete_resolver(
    id: str, roles: List[str], Model: Document, success_message: str, info: Info
):
    try:
        customer = None
        if "customer" in roles:
            customer = await get_verified_customer(info)
            if not customer:
                return Error(status=401, message="Forbidden!")

        query = Model.find({"_id": PydanticObjectId(id)})

        if customer:
            query.find({"customer_id": str(customer.id)})

        record = await query.first_or_none()

        if not record:
            return Error(status=404, message="Not Found!")

        await record.delete()

        return Error(status=200, message=success_message)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
    
