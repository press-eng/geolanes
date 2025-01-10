from typing import Annotated, Union

import strawberry

from lib.graphql.resolvers import customer_resolver, gl_admin_resolver, payment_resolver
from lib.graphql.types.all_customers_page import AllCustomersPage
from lib.graphql.types.all_payment_records_page import AllPaymentRecordsPage
from lib.graphql.types.chart_data_type import ChartDataError, ChartDataResponseType
from lib.graphql.types.error import Error
from lib.graphql.types.gl_admin import GlAdmin
from lib.graphql.types.revenue_page import RevenuePage


@strawberry.type
class GlAdminQuery:
    Gl_admin: Annotated[Union[GlAdmin, Error], strawberry.union("GlAdminResponse")] = (
        strawberry.field(resolver=gl_admin_resolver.read_gl_admin)
    )
    All_customers: Annotated[
        Union[AllCustomersPage, Error], strawberry.union("AllCustomersResponse")
    ] = strawberry.field(resolver=customer_resolver.read_all_customers)

    All_payment_records: Annotated[
        Union[AllPaymentRecordsPage, Error],
        strawberry.union("AllPaymentRecordsResponse"),
    ] = strawberry.field(resolver=payment_resolver.read_all_customer_payments)

    Revenue: Annotated[
        Union[RevenuePage, Error], strawberry.union("RevenueResponse")
    ] = strawberry.field(resolver=payment_resolver.revenue_generated)

    Revenue_chart_data: Annotated[
        Union[ChartDataResponseType, ChartDataError],
        strawberry.union("ChartDataResponse"),
    ] = strawberry.field(resolver=payment_resolver.admin_revenue_chart_data)

    Dashboard_data: Error = strawberry.field(
        resolver=gl_admin_resolver.show_dashboard_data
    )
