from typing import Optional

import strawberry


@strawberry.input
class DeleteGlAdminInput:
    permanent: Optional[bool] = strawberry.UNSET
    gl_admin_id: Optional[strawberry.ID] = strawberry.UNSET
