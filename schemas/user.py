from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from pydantic.alias_generators import to_camel


class RegisterSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    phone_number: str = Field(pattern=r'^09\d{9}$')

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class SignInSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    email: EmailStr
    password: str

class UserExistenceResponse(BaseModel):

    send: bool
    email:EmailStr
    phone_number: str


class RegisterSchemaResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    role: str
    status: str


class VerifyUserSchema(BaseModel):
    code: str
    email: EmailStr

class ResendOtpCode(BaseModel):
    email: EmailStr

class ResendOtpCodeResponse(BaseModel):
    email: EmailStr
    resend: bool
      
class TokenResponseModel(BaseModel):
    access_token: str
    token_type: str