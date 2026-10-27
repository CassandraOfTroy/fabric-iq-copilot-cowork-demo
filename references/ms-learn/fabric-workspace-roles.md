Source: https://learn.microsoft.com/fabric/fundamentals/roles-workspaces
Fetched: 2026-10-13

# Roles in workspaces in Microsoft Fabric

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Roles in workspaces in Microsoft Fabric

Workspace roles let you manage who can do what in a Microsoft Fabric workspace. Microsoft Fabric workspaces sit on top of OneLake and divide the data lake into separate containers that can be secured independently. Workspace roles in Microsoft Fabric extend the Power BI workspace roles by associating new Microsoft Fabric capabilities such as data integration and data exploration with existing workspace roles. For more information on Power BI roles, see [Roles in workspaces in Power BI](/en-us/power-bi/collaborate-share/service-new-workspaces).

You can either assign roles to individuals or to security groups, Microsoft 365 groups, and distribution lists. To grant access to a workspace, assign those user groups or individuals to one of the workspace roles: Admin, Member, Contributor, or Viewer. Here's how to [give users access to workspaces](give-access-workspaces). Microsoft Entra ID service principals (app registrations) can also be assigned to workspace roles and inherit the same permissions as users for API-based operations in Fabric, including the Items REST API and the Job Scheduler API.

To create a new workspace, see [Create a workspace](create-workspaces).

Everyone in a user group gets the role that you assign. If someone is in several user groups, they get the highest level of permission that's provided by the roles that they're assigned. If you nest user groups and assign a role to a group, all the contained users have permissions.

Users in workspace roles have the following Microsoft Fabric capabilities, in addition to the existing Power BI capabilities associated with these roles.

## Microsoft Fabric workspace roles

| Capability | Admin | Member | Contributor | Viewer |
| --- | --- | --- | --- | --- |
| Update and delete the workspace. | â |  |  |  |
| Add or remove people, including other admins. | â |  |  |  |
| Add members or others with lower permissions. | â | â |  |  |
| Allow others to reshare items.1 | â | â |  |  |
| Create or modify database items. | â | â | â |  |
| Create or modify database mirroring items. | â | â | â |  |
| Create or modify warehouse items. | â | â | â |  |
| Create workspace identity | â |  |  |  |
| Connect workspace to a Git repository | â |  |  |  |
| View and read content of pipelines, notebooks, Spark job definitions, ML models and experiments, and eventstreams. | â | â | â | â |
| View and read content of KQL databases, KQL query-sets, digital twin builder items, and real-time dashboards. | â | â | â | â |
| View and read content of event schema sets.5 | â | â | â | â |
| Connect to SQL analytics endpoint of Lakehouse or the Warehouse | â | â | â | â |
| Read Lakehouse and Data warehouse data and shortcuts2 with T-SQL through TDS endpoint (ReadData). | â | â | â | â |
| Read Lakehouse and Data warehouse data and shortcuts2 through OneLake APIs and Spark (ReadAll). | â | â | â |  |
| Read Lakehouse data through Lakehouse explorer (ReadAll). | â | â | â |  |
| Subscribe to OneLake events. | â | â | â |  |
| Write or delete pipelines, notebooks, Spark job definitions, ML models, and experiments, and eventstreams. | â | â | â |  |
| Write or delete Eventhouses3, KQL Querysets, Real-Time Dashboards, digital twin builder data, and schema and data of KQL Databases, Lakehouses, data warehouses, and shortcuts. | â | â | â |  |
| Create, write, or delete event schema sets, and the schemas and event types they contain.5 | â | â | â |  |
| Execute or cancel execution of notebooks, Spark job definitions, ML models, and experiments. | â | â | â |  |
| Execute or cancel execution of pipelines. | â | â | â |  |
| View execution output of pipelines, notebooks, ML models and experiments. | â | â | â | â |
| Schedule data refreshes via the on-premises gateway.4 | â | â | â |  |
| Modify gateway connection settings.4 | â | â | â |  |

1 Contributors and Viewers can also share items in a workspace, if they have Reshare permissions.

2 Other permissions are needed to read data from shortcut destination. Learn more about [shortcut security model.](../onelake/onelake-shortcuts?#types-of-shortcuts)

3 Other permissions are needed to perform certain operations on data in an Eventhouse. Learn more about the [hybrid role-based access control model](/en-us/kusto/access-control/role-based-access-control?view=microsoft-fabric&preserve-view=true).

4 Keep in mind that you also need permissions on the gateway. Those permissions are managed elsewhere, independent of workspace roles and permissions.

5 Publishing and consuming business event data is governed separately by data access roles, not by workspace roles. Learn more about [managing data access for business events](../real-time-hub/business-events/manage-business-events-data-access).

Note

The Create/Modify and Write/Delete permissions for notebooks apply equally when using the Items REST API. Admin, Member, and Contributor can perform notebook CRUD operations via the API, while Viewer cannot. For Job Scheduler API execution, Admin, Member, and Contributor can start and cancel runs; all roles including Viewer can monitor run status and view execution output, including run metadata such as status and exit values returned by notebook runs.

## Related content

- [Roles in workspaces in Power BI](/en-us/power-bi/collaborate-share/service-new-workspaces)
- [Create workspaces](create-workspaces)
- [Give users access to workspaces](give-access-workspaces)
- [Fabric and OneLake security](../onelake/security/fabric-onelake-security)
- [OneLake shortcuts](../onelake/onelake-shortcuts?#types-of-shortcuts)
- [Data warehouse security](../data-warehouse/workspace-roles)
- [Data engineering security](../data-engineering/workspace-roles-lakehouse)
- [Data science roles and permissions](../data-science/models-experiments-rbac)
- [Role-based access control in Eventhouse](/en-us/kusto/access-control/role-based-access-control?view=microsoft-fabric&preserve-view=true)

---

- Last updated on 
  2026-08-18
