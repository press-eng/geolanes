from beanie import PydanticObjectId
from beanie.operators import In
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_followed_customer_input import (
    CreateFollowedCustomerInput,
)
from lib.graphql.inputs.delete_followed_input import DeleteFollowedInput
from lib.graphql.inputs.delete_follower_input import DeleteFollowerInput
from lib.graphql.inputs.followed_customer_input import FollowedCustomerInput
from lib.graphql.inputs.follower_input import FollowerInput
from lib.graphql.inputs.friend_suggestion_input import FriendSuggestionInput
from lib.graphql.types.customer_public_page import CustomerPublicPage
from lib.graphql.types.error import Error
from lib.helpers.customer_helper import (
    customer_model_to_public_type,
    get_verified_customer,
)
from lib.models.customer_friend_model import CustomerFriendModel
from lib.models.customer_model import CustomerModel
from lib.services.my_fb_auth import get_facebook_friends


async def create_followed_customer(customer: CreateFollowedCustomerInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        friend_customer = await CustomerModel.get(customer.customer)
        if not friend_customer:
            return Error(status=400, message="Invalid customer ID!")

        friend_record = await CustomerFriendModel.find(
            CustomerFriendModel.follower_customer_id == str(verified_customer.id),
            CustomerFriendModel.followed_customer_id == customer.customer,
        ).first_or_none()
        if friend_record:
            return Error(status=400, message="You cannot follow a customer twice!")

        if verified_customer.id == friend_customer.id:
            return Error(status=400, message="Cannot add yourself as friend!")

        await CustomerFriendModel.insert_one(
            CustomerFriendModel(
                follower_customer_id=str(verified_customer.id),
                followed_customer_id=customer.customer,
            )
        )

        return Error(status=201, message="Created followed customer succesfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_followed_customers(customers: FollowedCustomerInput, info: Info):
    page = customers.page or 1

    try:
        verified_customer = await get_verified_customer(info)

        friend_query = (
            CustomerFriendModel.find(
                CustomerFriendModel.follower_customer_id == str(verified_customer.id)
            )
            .limit(config.PAGE_SIZE)
            .skip(config.PAGE_SIZE * (page - 1))
        )
        friend_records = await friend_query.to_list()

        friend_customers = await CustomerModel.find(
            In(
                CustomerModel.id,
                [PydanticObjectId(f.followed_customer_id) for f in friend_records],
            )
        ).to_list()

        return CustomerPublicPage(
            items=[customer_model_to_public_type(c) for c in friend_customers],
            page=page,
            total=await friend_query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_followed_customer(customer: DeleteFollowedInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        friend = await CustomerFriendModel.find(
            CustomerFriendModel.follower_customer_id == str(verified_customer.id),
            CustomerFriendModel.followed_customer_id == customer.customer,
        ).first_or_none()

        if not friend:
            return Error(status=404, message="Invalid followed customer ID!")

        await friend.delete()

        return Error(status=200, message="Unfollowed successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_followers(followers: FollowerInput, info: Info):
    page = followers.page or 1

    try:
        verified_customer = await get_verified_customer(info)

        query = (
            CustomerFriendModel.find(
                CustomerFriendModel.followed_customer_id == str(verified_customer.id)
            )
            .limit(config.PAGE_SIZE)
            .skip(config.PAGE_SIZE * (page - 1))
        )
        friend_records = await query.to_list()

        friend_customers = await CustomerModel.find(
            In(
                CustomerModel.id,
                [PydanticObjectId(c.follower_customer_id) for c in friend_records],
            )
        )

        return CustomerPublicPage(
            items=[await customer_model_to_public_type(c) for c in friend_customers],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_follower(follower: DeleteFollowerInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        friend = await CustomerFriendModel.find(
            CustomerFriendModel.followed_customer_id == str(verified_customer.id),
            CustomerFriendModel.follower_customer_id == follower.customer,
        ).first_or_none()

        if not friend:
            return Error(status=404, message="Follower not found!")

        await friend.delete()

        return Error(status=200, message="Follower removed successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_friend_suggestions(friends: FriendSuggestionInput, info: Info):
    page = friends.page or 1

    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        if (
            len(
                [
                    f
                    for f in [
                        friends.just_contacts,
                        friends.just_coordinates,
                        friends.just_facebook,
                    ]
                    if f
                ]
            )
            > 1
        ):
            return Error(status=400, message="Only one of just_* filter is required.")

        followed_customers = await CustomerFriendModel.find(
            CustomerFriendModel.follower_customer_id == str(customer.id)
        ).to_list()

        followed_customer_ids = [
            PydanticObjectId(friend.followed_customer_id)
            for friend in followed_customers
        ]

        query = (
            CustomerModel.find(CustomerModel.is_private == False)
            .skip(config.PAGE_SIZE * (page - 1))
            .limit(config.PAGE_SIZE)
        )

        query = query.find({"_id": {"$nin": followed_customer_ids}})

        if friends.just_facebook:
            try:
                facebook_friend_ids = await get_facebook_friends(customer)
                query = query.find(In(CustomerModel.facebook_id, facebook_friend_ids))
            except Exception as e:
                print(e)
                return Error(status=500, message="Failed to fetch Facebook friends")

        if friends.just_contacts:
            query = query.find(In(CustomerModel.phone, customer.contacts))

        if friends.just_coordinates:
            query = query.find(
                CustomerModel.address_latitude < friends.just_coordinates.lat + 2,
                CustomerModel.address_latitude > friends.just_coordinates.lat - 2,
                CustomerModel.address_longitude < friends.just_coordinates.lng + 2,
                CustomerModel.address_longitude > friends.just_coordinates.lng - 2,
            )

        if friends.search:
            query = query.find({"$text": {"$search": friends.search}})

        return CustomerPublicPage(
            items=[customer_model_to_public_type(c) for c in await query.to_list()],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
