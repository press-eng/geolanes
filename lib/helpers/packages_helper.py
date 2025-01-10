from lib.graphql.types.package import Package
from lib.models.package_model import PackageModel


async def packages_model_to_type(model: PackageModel) -> Package:
    return Package(
        id=str(model.id),
        title=model.title,
        featured_content=model.featured_content,
        view_tiles=model.view_tiles,
        save_impressions=model.save_impressions,
        review_itineraries=model.review_itineraries,
        integerated_ads=model.integerated_ads,
        create_itinerary=model.create_itinerary,
        start_itinerary=model.start_itinerary,
        search_with_ai=model.search_with_ai,
        share_itinerary=model.share_itinerary,
        content_contributor=model.content_contributor,
        create_subscriber_group=model.create_subscriber_group,
        monetize_itinerary=model.monetize_itinerary,
        analytics=model.analytics,
        single_layer_content_categories=model.single_layer_content_categories,
        multi_layer_content_categories=model.multi_layer_content_categories,
        tile_limit=model.tile_limit,
        push_notifications=model.push_notifications,
        api_integerations=model.api_integerations,
        web_administrator_portal=model.web_administrator_portal,
        price=model.price,
        status=model.status,
        updated_at=model.updated_at,
    )
