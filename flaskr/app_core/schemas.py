from marshmallow import Schema, fields, validate


def get_src_schema(src_required=False):
    return type('SrcSchema', (Schema,), {
        'src': fields.String(validate=validate.Length(min=3, max=20), required=src_required)})
