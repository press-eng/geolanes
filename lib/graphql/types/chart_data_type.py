from typing import Dict, List, Optional

import strawberry


@strawberry.type
class MonthData:
    month: str
    amount: int


@strawberry.type
class CustomerDataset:
    customerType: str
    data: List[MonthData]


@strawberry.type
class SummaryEntry:
    customerType: str
    total: int
    percentage: Optional[str] = None


@strawberry.type
class ChartDataResponseType:
    status: str
    datasets: List[CustomerDataset]
    summary: List[SummaryEntry]


@strawberry.type
class ChartDataError:
    message: str
