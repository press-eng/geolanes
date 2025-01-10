from typing import Any, Dict, Union

from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_payment_input import CreatePaymentInput
from lib.graphql.types.all_payment_records_page import AllPaymentRecordsPage
from lib.graphql.types.chart_data_type import (
    ChartDataError,
    ChartDataResponseType,
    CustomerDataset,
    MonthData,
    SummaryEntry,
)
from lib.graphql.types.error import Error
from lib.graphql.types.payment import Payment
from lib.graphql.types.revenue import Revenue
from lib.graphql.types.revenue_page import RevenuePage
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.gl_admin_helper import get_verified_gl_admin
from lib.helpers.payment_helper import payment_model_to_type
from lib.models.customer_model import CustomerModel
from lib.models.enterprise_customer_model import EnterpriseCustomerModel
from lib.models.payment_model import PaymentModel
from lib.services import my_stripe_client


async def create_payment(record: CreatePaymentInput, info: Info):
    try:
        customer = await get_verified_customer(info)

        if not customer:
            return Error(status=403, message="Forbidden!")

        if not record.payment_amount:
            return Error(status=400, message="Invalid payment amount")

        if not record.payment_currency:
            return Error(status=400, message="Invalid payment currency")

        intent = await my_stripe_client.create_stripe_payment_intent(
            customer.id, record.payment_amount, record.payment_currency
        )

        customer_detail = await CustomerModel.find_one(
            {"_id": PydanticObjectId(customer.id)}
        )
        if customer_detail:
            pay_customer_type = "Individual"
        else:
            ent_customer_detail = await EnterpriseCustomerModel.find_one(
                {"_id": PydanticObjectId(input.id)}
            )
            if ent_customer_detail:
                pay_customer_type = ent_customer_detail.account_type

        payment = await PaymentModel.insert_one(
            PaymentModel(
                customer_id=str(customer.id),
                amount=record.payment_amount,
                currency=record.payment_currency,
                payment_status="created",
                payment_intent_id=intent["id"],
                customer_type=pay_customer_type,
            )
        )

        return Payment(
            customer_id=payment.customer_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_status=payment.payment_status,
            customer_type=payment.customer_type,
            payment_intent_id=intent["client_secret"],
        )

    except Exception as e:
        print(e)
        return Error(status=400, message=f"Something went wrong! - {e}")


async def read_customer_payments(page: int, info: Info):
    try:
        customer = await get_verified_customer(info)

        if not customer:
            return Error(status=403, message="Forbidden!")

        payments = await PaymentModel.find(
            PaymentModel.customer_id == str(customer.id)
        ).to_list()

        return AllPaymentRecordsPage(
            items=[await payment_model_to_type(p) for p in payments],
            total=len(payments),
            page=page,
        )

    except Exception as e:
        print(e)
        return Error(status=400, message=str(e))


async def read_all_customer_payments(page: int, info: Info):
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        query = (
            PaymentModel.find()
            .limit(config.PAGE_SIZE)
            .skip((page - 1) * config.PAGE_SIZE)
        )
        payments = await query.to_list()

        return AllPaymentRecordsPage(
            items=[await payment_model_to_type(p) for p in payments],
            total=query.count(),
            page=page,
        )

    except Exception as e:
        print(e)
        return Error(status=400, message="Something went wrong!")


async def revenue_generated(info: Info) -> Revenue:
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        payments = await PaymentModel.find(PaymentModel.status == "succeeded").to_list()

        if not payments:
            return Error(status=400, message="No successful transactions")

        monthly_totals = {}
        grand_total = 0.0

        for payment in payments:
            payment_date = payment.updated_at
            month_year = payment_date.strftime("%Y-%m")

            amount = payment.amount

            if month_year in monthly_totals:
                monthly_totals[month_year] += amount
            else:
                monthly_totals[month_year] = amount

            grand_total += amount

        monthly_revenues = [
            Revenue(month=month, total=total)
            for month, total in sorted(monthly_totals.items())
        ]

        revenue_summary = RevenuePage(
            monthly_revenues=monthly_revenues, grand_total=grand_total
        )

        return revenue_summary

    except Exception as e:
        print(e)
        return Error(status=400, message="Something went wrong!")


async def admin_revenue_chart_data(
    info: Info,
) -> Union[ChartDataResponseType, ChartDataError]:
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        pipeline = [
            {"$match": {"payment_status": "created"}},
            {
                "$addFields": {
                    "month": {"$month": "$updated_at"},
                    "year": {"$year": "$updated_at"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month",
                        "customer_type": "$customer_type",
                    },
                    "total_amount": {"$sum": "$amount"},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]

        results = await PaymentModel.aggregate(pipeline).to_list()

        datasets = {}
        for result in results:
            year_month = f"{result['_id']['year']}-{result['_id']['month']:02d}"
            customer_type = result["_id"]["customer_type"]
            amount = result["total_amount"]

            if customer_type not in datasets:
                datasets[customer_type] = []

            datasets[customer_type].append(MonthData(month=year_month, amount=amount))

        dataset_list = [
            CustomerDataset(customerType=k, data=v) for k, v in datasets.items()
        ]

        summary_list = []
        for dataset in dataset_list:
            customer_type = dataset.customerType
            data = dataset.data

            total_amount = sum(month_data.amount for month_data in data)

            percentage = None
            if len(data) >= 2:
                old_amount = sum(month_data.amount for month_data in data[:-1])
                new_amount = data[-1].amount

                if old_amount != 0:

                    change_percent = ((new_amount - old_amount) / old_amount) * 100
                else:

                    change_percent = -100.00

                percentage = f"{change_percent:.2f}%"

            summary_list.append(
                SummaryEntry(
                    customerType=customer_type,
                    total=total_amount,
                    percentage=percentage,
                )
            )

        return ChartDataResponseType(
            status="success",
            datasets=dataset_list,
            summary=summary_list,
        )

    except Exception as e:
        return ChartDataError(message=str(e))
