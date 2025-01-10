from typing import Optional

from lib import config
from lib.graphql.inputs.package_input import PackageInput
from lib.graphql.types.error import Error
from lib.graphql.types.package_page import PackagePage
from lib.helpers.packages_helper import packages_model_to_type
from lib.models.package_model import PackageModel


async def read_packages(packages: Optional[PackageInput] = None):
    packages = packages or PackageInput(page=1)

    try:
        searched_packages = (
            await PackageModel.find_all()
            .skip((packages.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = await PackageModel.find_all().count()

        return PackagePage(
            items=[await packages_model_to_type(n) for n in searched_packages],
            page=packages.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
