from flask import g
from oslo_serialization import jsonutils
from oslo_log import log

from craton.api.v1 import base
from craton import db as dbapi
from craton import util


LOG = log.getLogger(__name__)


class Regions(base.Resource):

    @base.http_codes
    @base.filtered_context()
    def get(self, context, **filters):
        """Get region(s) for the project. Get region details if
        for a particular region.
        """
        region_id = filters.get("id")
        region_name = filters.get("name")

        if not region_id and not region_name:
            # Get all regions for this tenant
            regions_obj = dbapi.regions_get_all(context, filters)
            return jsonutils.to_primitive(regions_obj), 200, None

        if region_name:
            region_obj = dbapi.regions_get_by_name(context, region_name)
            region_obj.data = region_obj.variables
            return jsonutils.to_primitive([region_obj]), 200, None

        if region_id:
            region_obj = dbapi.regions_get_by_id(context, region_id)
            region_obj.data = region_obj.variables
            return jsonutils.to_primitive([region_obj]), 200, None

    @base.http_codes
    def post(self, context):
        """Create a new region."""
        json = util.copy_project_id_into_json(context, g.json)
        region_obj = dbapi.regions_create(context, json)
        region = jsonutils.to_primitive(region_obj)
        if 'variables' in json:
            region["variables"] = jsonutils.to_primitive(region_obj.variables)
        else:
            region["variables"] = {}
        return region, 200, None


class RegionsById(base.Resource):

    @base.http_codes
    def get(self, context, id):
        region_obj = dbapi.regions_get_by_id(context, id)
        region = jsonutils.to_primitive(region_obj)
        region['variables'] = jsonutils.to_primitive(region_obj.variables)
        return region, 200, None

    def put(self, context, id):
        """Update existing region."""
        region_obj = dbapi.regions_update(context, id, g.json)
        return jsonutils.to_primitive(region_obj), 200, None

    @base.http_codes
    def delete(self, context, id):
        """Delete existing region."""
        dbapi.regions_delete(context, id)
        return None, 204, None


class RegionsVariables(base.Resource):

    @base.http_codes
    def get(self, context, id):
        """Get variables for given region."""
        obj = dbapi.regions_get_by_id(context, id)
        response = {"variables": jsonutils.to_primitive(obj.variables)}
        return response, 200, None

    @base.http_codes
    def put(self, context, id):
        """
        Update existing region variables, or create if it does
        not exist.
        """
        obj = dbapi.regions_variables_update(context, id, g.json)
        response = {"variables": jsonutils.to_primitive(obj.variables)}
        return response, 200, None

    @base.http_codes
    def delete(self, context, id):
        """Delete region variables."""
        dbapi.regions_variables_delete(context, id, g.json)
        return None, 204, None
