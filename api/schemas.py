from marshmallow import Schema, fields


class ProductIdSchema(Schema):
    product_id = fields.String(required=True)


class UrlsDataSchema(ProductIdSchema):
    images_urls = fields.List(fields.URL, required=True)


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserRegisterSchema(UserLoginSchema):
    name = fields.String(required=True)
    last_name = fields.String(required=True)
