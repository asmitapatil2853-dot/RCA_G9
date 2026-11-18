// Neo4j Graph Database Schema & RCA Topology Ingestion
MATCH (n) DETACH DELETE n;
CREATE (API_Gateway:Service {name: 'API-Gateway', layer: 'Edge-Gateway', rca_status: 'AFFECTED_OR_HEALTHY'});
CREATE (Auth_Service:Service {name: 'Auth-Service', layer: 'Microservice', rca_status: 'AFFECTED_OR_HEALTHY'});
CREATE (Order_Service:Service {name: 'Order-Service', layer: 'Microservice', rca_status: 'AFFECTED_OR_HEALTHY'});
CREATE (Database_Service:Service {name: 'Database-Service', layer: 'Relational-DB', rca_status: 'ROOT_CAUSE'});
CREATE (K8s_Infra_Node:Service {name: 'K8s-Infra-Node', layer: 'Infrastructure', rca_status: 'ROOT_CAUSE'});
CREATE (API_Gateway)-[:DEPENDS_ON]->(Auth_Service);
CREATE (API_Gateway)-[:DEPENDS_ON]->(Order_Service);
CREATE (Order_Service)-[:DEPENDS_ON]->(Database_Service);
CREATE (Auth_Service)-[:DEPENDS_ON]->(K8s_Infra_Node);
CREATE (Database_Service)-[:DEPENDS_ON]->(K8s_Infra_Node);