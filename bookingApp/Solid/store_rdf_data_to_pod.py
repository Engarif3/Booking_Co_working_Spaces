def store_rdf_data_to_pod(auth_session, pod_url, rdf_data):
    """Store RDF data in a Solid POD using an authenticated session."""
    headers = {'Content-Type': 'text/turtle'}
    response = auth_session.put(pod_url, data=rdf_data, headers=headers)
    
    return response.status_code, response.reason


