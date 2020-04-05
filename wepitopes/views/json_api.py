import wepitopes.models.db_collections as COL

from pyramid.view import view_config
from ..database import get_database
from . import useful as us
from .. import configuration as conf

@view_config(route_name='api_get_fields', renderer='jsonp')
def get_fields(request):
    """
    returns possible all fields for subsetting
    {limit: 5000} will limit the number of
    field for enumerations to the 5000 first. Otherwise
    the maximum is the used is the one defined the configuration
    of the back end
    """
    limit = conf.DEFAULT_ENUMERATION_LIMIT
    if 'limit' in request.json:
        try :
            limit = int(request.json["limit"])
        except Exception as e:
            us.JSONResponse(errors = ["limit must be a valid integer"])

    db = get_database()
    check, payload = us.get_fields(db, COL.__COLLECTIONS.values(), limit)
    if not check:
        return us.JSONResponse(errors = payload)

    ret = us.JSONResponse() 
    ret.set_payload(payload)
    return ret

@view_config(route_name='api_get_fields_limit', renderer='jsonp')
def get_fields_limit(request):
    """
    returns possible all fields.
    'limit=5000' will limit the number of
    field for enumerations to the 5000 first.
    """
    try:
        limit = int(request.matchdict['limit'])
    except Exception as e:
        us.JSONResponse(errors = ["limit must be a valid integer"])
    
    db = get_database()
    check, payload = us.get_fields(db, COL.__COLLECTIONS.values(), limit)
    if not check:
        return us.JSONResponse(errors = payload)

    ret = us.JSONResponse() 
    ret.set_payload(payload)
    return ret

@view_config(route_name='api_get_collection_fields_limit', renderer='jsonp')
def get_collection_fields_limit(request):
    """
    returns possible all fields for a collection
    'limit=5000' will limit the number of
    field for enumerations to the 5000 first.
    """
    try:
        limit = int(request.matchdict['limit'])
    except Exception as e:
        us.JSONResponse(errors = ["limit must be a valid integer"])
    
    db = get_database()

    try:
        colname = request.matchdict['collection']
        collection = COL.__COLLECTIONS[colname]#db[colname].__class__
    except Exception as e:
        return us.JSONResponse(errors = ["Collection name must be valid"])
    
    check, payload = us.get_fields(db, [collection], limit)
    if not check:
        return us.JSONResponse(errors = payload)
    ret = us.JSONResponse() 
    ret.set_payload(payload)
    return ret

# def get_fields(request):
#     """
#     returns possible all fields for subsetting
#     {limit: 5000} will limit the number of
#     field for enumerations to the 5000 first. Otherwise
#     the maximum is the used is the one defined the configuration
#     of the back end
#     """
    
#     limit = conf.DEFAULT_ENUMERATION_LIMIT
#     try :
#         if 'limit' in request.json:
#             limit = request.json["limit"]
#     except :
#         pass 
        
#     db = get_database()
#     payload = {}
#     for col_cls in COL.__COLLECTIONS:
#         col_name = col_cls.__name__
#         payload[col_name] = {}
#         for field_name in col_cls._fields.keys():
#             typ = col_cls._field_types.get(field_name)
#             if typ=="float":
#                 field_dct = {"type": typ}
#                 min_val = us.get_extremum(db, col_name, field_name, "ASC")
#                 max_val = us.get_extremum(db, col_name, field_name, "DESC")
#                 field_dct["range"] = [min_val, max_val]
#             elif typ=="enumeration":
#                 field_dct = {"type": typ}
#                 try:
#                     field_dct.update(us.get_enumeration(db, col_name, field_name, limit))
#                 except:
#                     return us.JSONResponse(errors = ["Invalid request for field %s of %s" % (field_name, col_name)] ) 
#             else:
#                 field_dct = {"type": "other"}
            
#             payload[col_name][field_name] = field_dct
    
#     ret = us.JSONResponse() 
#     ret.set_payload(payload)
#     return ret

@view_config(route_name='api_get_data', renderer='jsonp')
def get_data(request):
    json_data = request.json
    
    try:
        check, aql_or_message = us.build_query(json_data["payload"], print_aql=False)
    except Exception as e:
        return us.JSONResponse(errors = ["Unable to prossess requests. Please verify format"] )
        
    if not check:
        return us.JSONResponse(errors = [aql_or_message] )

    db = get_database()
    result = db.AQLQuery(aql_or_message, rawResults=True, batchSize=conf.DEFAULT_BATCH_SIZE, bindVars={})
    
    ret = us.JSONResponse()
    ret.set_payload(result.result)
    return ret
