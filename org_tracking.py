import json

def runner(context, basicIO):
    moduleObject = json.loads(basicIO.getParameter("shipment_order"))
    context.log.INFO(moduleObject)
    organizationObject = json.loads(basicIO.getParameter("organization"))
    context.log.INFO("Organization ID " + organizationObject["organization_id"])