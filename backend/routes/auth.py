from fastapi import APIRouter, Depends, HTTPException
import boto3

from db.models.user import User
from db.db import get_db
from helper.auth_helper import get_secret_hash
from pydantic_models.auth_models import (
    ConfirmSignupRequest,
    LoginRequest,
    SignupRequest,
)
from secrets_keys import SecretsKeys
from sqlalchemy.orm import Session

router = APIRouter()
secret_keys = SecretsKeys()

COGNITO_CLIENT_ID = secret_keys.COGNITO_CLIENT_ID
COGNITO_CLIENT_SECRET = secret_keys.COGNITO_CLIENT_SECRET


cognito_client = boto3.client("cognito-idp", region_name=secret_keys.REGION_NAME)


@router.post("/signup")
def signup_user(data: SignupRequest, db: Session = Depends(get_db)):

    try:
        secret_hash = get_secret_hash(
            data.email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
        )
        cognito_response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=data.email,
            Password=data.password,
            SecretHash=secret_hash,
            UserAttributes=[
                {"Name": "email", "Value": data.email},
                {"Name": "name", "Value": data.name},
            ],
        )

        cognito_sub = cognito_response.get("UserSub")
        if not cognito_sub:
            raise HTTPException(400, "Cognito did not return a valid user sub")

        new_user = User(name=data.name, email=data.email, cognito_sub=cognito_sub)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"msg": "Signup succesful. Please verify your email if required."}
    except Exception as e:
        raise HTTPException(400, f"Cognito signup exception: {e} ")


@router.post("/login")
def login_user(data: LoginRequest):

    try:
        secret_hash = get_secret_hash(
            data.email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
        )
        cognito_response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": data.email,
                "PASSWORD": data.password,
                "SECRET_HASH": secret_hash,
            },
        )

        return {"message": "User login successfully"}
    except Exception as e:
        raise HTTPException(400, f"Cognito signup exception: {e} ")


@router.post("/confirm-signup")
def confirm_signup(data: ConfirmSignupRequest):

    try:
        secret_hash = get_secret_hash(
            data.email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
        )
        cognito_response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.otp,
            SecretHash=secret_hash,
        )
        return {"message": "User confirmed successfully"}
    except Exception as e:
        raise HTTPException(400, f"Cognito signup exception: {e} ")
