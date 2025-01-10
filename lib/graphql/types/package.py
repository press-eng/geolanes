from datetime import datetime

import strawberry


@strawberry.type
class Package:
    id: strawberry.ID
    title: str
    featured_content: bool
    view_tiles: bool
    save_impressions: bool
    review_itineraries: bool
    integerated_ads: bool
    create_itinerary: bool
    start_itinerary: int
    search_with_ai: int
    share_itinerary: bool
    content_contributor: bool
    create_subscriber_group: bool
    monetize_itinerary: bool
    analytics: bool
    single_layer_content_categories: bool
    multi_layer_content_categories: bool
    tile_limit: int
    push_notifications: bool
    api_integerations: bool
    web_administrator_portal: bool
    price: int
    status: str
    updated_at: datetime
