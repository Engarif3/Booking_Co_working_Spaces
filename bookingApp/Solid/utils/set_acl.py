def set_acl(solid_session, user_pod_url, user_webid):
    acl_data = f"""
    @prefix acl: <http://www.w3.org/ns/auth/acl#>.
    @prefix foaf: <http://xmlns.com/foaf/0.1/>.

    <#owner>
        a acl:Authorization;
        acl:agent "{user_webid}";
        acl:accessTo <./>;
        acl:mode acl:Read, acl:Write, acl:Control.

    <#public>
        a acl:Authorization;
        acl:agentClass foaf:Agent;
        acl:accessTo <./>;
        acl:mode acl:Read.
    """
    acl_url = user_pod_url + '.acl' 
    response = solid_session.put(acl_url, data=acl_data, headers={"Content-Type": "text/turtle"})
    return response.ok
