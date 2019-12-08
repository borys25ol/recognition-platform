from marshmallow import Schema, fields


class ProductIdSchema(Schema):
    product_id = fields.String(required=True)


class UrlsDataSchema(ProductIdSchema):
    images_urls = fields.List(fields.URL, required=True)



