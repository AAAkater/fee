from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db.main import SessionDep
from app.models.db_models.user import UserCreate
from app.models.request.user import UserRegisterBody
from app.models.response import ResponseBase
from app.models.response.user import TokenItem
from app.services import user_service
from app.utils import security
from app.utils.logger import logger
from app.utils.security import Captcha
from app.utils.token import create_access_token

router = APIRouter(tags=["user"])


@router.post(
    "/login",
    response_model=ResponseBase[TokenItem],
    summary="User login",
)
async def login(
    session: SessionDep,
    user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> ResponseBase[TokenItem]:
    """
    Authenticates a user and returns an access token.

    Args:
        session (SessionDep): Database session dependency.
        user_form (Annotated[OAuth2PasswordRequestForm, Depends()]): Form containing username and password.

    Returns:
        ResponseBase[TokenItem]: Response containing the access token with type 'Bearer'.

    Raises:
        HTTPException: If user authentication fails (400 status code).

    Notes:
        - Uses OAuth2 password flow for authentication.
        - Logs errors if user retrieval fails.
        - Generates JWT access token for authenticated users.
    """
    try:
        user = user_service.get_user_by_username(
            session=session,
            username=user_form.username,
        )
    except Exception as e:
        logger.error(f"Failed to obtain user information:\n{e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    token = create_access_token(str(user.id))

    return ResponseBase[TokenItem](
        code="0",
        msg="ok",
        data=TokenItem(access_token=token, token_type="Bearer"),
    )


@router.post(
    "/register",
    status_code=status.HTTP_200_OK,
    response_model=ResponseBase,
    summary="User registration",
)
async def register(
    session: SessionDep, new_user: UserRegisterBody
) -> ResponseBase:
    """
    Registers a new user after validating captcha codes and username availability.

    Validates both email and image captcha codes, checks if the username is already taken,
    and creates a new user if all validations pass.

    Args:
        session (SessionDep): Database session dependency.
        new_user (UserRegisterBody): User registration data including:
            - username: Desired username
            - email: User's email address
            - password: User's password
            - email_captcha_code: Email verification code
            - img_captcha_id: Image captcha ID
            - img_captcha_code: Image captcha code

    Returns:
        ResponseBase: Empty response indicating successful registration.

    Raises:
        HTTPException:
            - 400 if email verification code is invalid
            - 400 if image verification code is invalid
            - 400 if username already exists
            - 500 if user creation fails
    """
    # Verify email verification code
    if not Captcha.verify_captcha(new_user.email, new_user.email_captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong email verification code",
        )

    # Verify image verification code
    if not Captcha.verify_captcha(
        new_user.img_captcha_id, new_user.img_captcha_code
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong image verification code",
        )

    # Check if the username already exists

    try:
        db_user = user_service.get_user_by_username(
            session=session, username=new_user.username
        )
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"The new username is not used:\n{e}")

    # Create a new user
    try:
        user_service.create_new_user(
            session=session,
            new_user_info=UserCreate(
                username=new_user.username,
                email=new_user.email,
                password_hash=security.get_password_hash(new_user.password),
            ),
        )
    except Exception as e:
        logger.error(f"Failed to register new user:\n{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register new user",
        )

    return ResponseBase()
