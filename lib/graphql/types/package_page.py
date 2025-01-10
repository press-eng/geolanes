from typing import List

import strawberry

from lib.graphql.types.package import Package


@strawberry.type
class PackagePage:
    items: List[Package]
    page: int
    total: int
