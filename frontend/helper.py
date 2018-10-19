import json
import pprint

swagger = json.loads(open('swagger-client-generated/swagger.json', 'rb').read())


pprint.pprint(swagger['paths']['/sites']['post']['parameters'])

