from pydantic import BaseModel, Field
from typing import Optional


class BaseSerializer(BaseModel):
	pass


class ResponseSerializer(BaseSerializer):
	is_success: bool
	request_id: str
	x_creator_id: str
	error_message: Optional[str]
	body: Optional[dict]


class RequestMessageSerializer(BaseModel):
	request_id: str = Field(alias='RequestId')
	service: str
	book_id: str = Field(alias='BookId')


class BookSerializer(BaseModel):
	author: str
	book_name: str = Field(alias='BookName')


class ResponseMessageSerializer(BaseModel):
	request_id: str = Field(alias='RequestId')
	book: BookSerializer
