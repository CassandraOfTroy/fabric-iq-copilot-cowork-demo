Source: https://learn.microsoft.com/power-bi/connect-data/service-datasets-permissions
Fetched: 2026-10-13

# Semantic model permissions

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Semantic model permissions

This article describes semantic model permissions in the Power BI service and how these permissions are acquired by users.

## What are the semantic model permissions?

The following table describes the four levels of permission that control access to semantic models in the Power BI service. The table also describes the permissions that the semantic model owner has on the semantic model, and other actions that only the semantic model owner can perform.

| Permission | Description |
| --- | --- |
| Read | Allows users to access and interact with reports and other solutions (such as composite models on Premium/PPU workspaces) that read data from the semantic model. This includes the ability to use the [Explore](../explore-reports/explore-data-service) feature to interact with the data in these semantic models. |
| Build | Allows user to build new content from the semantic model and find content that uses the semantic model. Allows user to access reports that access composite models on Power BI Pro workspaces. Allows user to build composite models. Allows user to pull the data into Analyze in Excel. Allows querying using external APIs such as XMLA. Allows user to see hidden data fields. |
| Reshare | Allows user to grant semantic model access. |
| Write | Allows user to republish the semantic model. Allows user to [backup and restore the semantic model](../enterprise/service-premium-backup-restore-dataset). Allows user to make changes to the semantic model via XMLA. Allows user to manually trigger a refresh of the semantic model using **Refresh now**. Allows user to edit semantic model settings, except scheduled refresh, credentials, and automatic aggregations. |
| Owner | The semantic model owner isn't a permission in itself, but rather a conceptual role that has all the permissions on a semantic model. The first semantic model owner is the person who created the semantic model, and afterwards the last person to configure the semantic model after taking it over in the semantic model settings.  In addition to the permissions described in this table that can be granted explicitly, only a semantic model owner can configure scheduled refresh, credentials, and automatic aggregations. |

Note

Build permission is primarily a discoverability feature. It enables users to easily discover semantic models and build Power BI reports and other consumable items based on the discovered models, such as Excel PivotTables and non-Microsoft data visualization tools, using the XMLA endpoint. Users who have Read permission without Build permission can consume and interact with existing reports that have been shared with them. Granting Read permission without Build permission should not be relied upon to secure sensitive data. Users with Read permission, even without Build permission, are able to access and interact with data in the semantic model.

## How are semantic model permissions acquired?

### Permissions acquired implicitly via workspace role

A user's role in a workspace implicitly grants them permissions on the semantic models in the workspace, as described in the following table.

|  | Admin | Member | Contributor | Viewer |
| --- | --- | --- | --- | --- |
| **Read** |  |  |  |  |
| **Build** |  |  |  |  |
| **Reshare** |  |  |  |  |
| **Write** |  |  |  |  |

Note

Permissions inherited via workspace role can only be changed or taken away from a user by changing or removing their role in the workspace. They can't be changed or removed explicitly using the [manage permissions page](service-datasets-manage-access-permissions).

### Licensing considerations for workspace roles

The ability to use semantic model permissions granted by workspace roles depends on workspace capacity and user licensing:

- **Workspaces in shared capacity**: All users require a Power BI Pro or Premium Per User (PPU) license to access semantic models, regardless of their workspace role.
- **Workspaces in Premium capacity**: Users with the Viewer role can access semantic models with a free license. Users with Admin, Member, or Contributor roles require a Pro or PPU license to create or edit content, but can view content with a free license.

For more information about workspace licensing, see [Roles and licenses in workspaces](../collaborate-share/service-new-workspaces#roles-and-licenses).

### Permissions granted explicitly via the manage semantic model permissions page

A user with an Admin or Member role in the workspace can explicitly grant permissions to other users using the [manage permissions page](service-datasets-manage-access-permissions).

Important

Granting explicit semantic model permissions does not automatically provide access to use those permissions. Users must also meet licensing requirements:

- By using Build permission, users without a Pro or PPU license can author reports from shared semantic models hosted on Power BI Premium or Fabric F64 or higher capacity. They access those models through OneLake Catalog, can store the reports only in **My workspace**, and can't share them.
- Users need a Pro or PPU license to store reports in another workspace or share the reports.

For more information, see [Licensing considerations for shared semantic models](service-datasets-across-workspaces#licensing).

### Permissions acquired via a link

When users share reports or semantic models, they create links that provide permissions on the semantic model. Users authorized to use those links can access the semantic model. Users with Admin or Member roles in the workspace where a semantic model is located can manage these links on the [manage permissions page](service-datasets-manage-access-permissions#manage-links).

### Permissions granted in an app

Users can acquire permissions on a semantic model used in an app if the app owner allows this in the [app permissions configuration](../collaborate-share/service-create-distribute-apps#create-and-manage-multiple-audiences).

### Permissions granted via REST APIs

Semantic model permissions can be set via REST APIs. For more information, see [Semantic model permissions in the context of the Power BI REST APIs](../developer/embedded/datasets-permissions).

## Semantic model permissions and row-level security (RLS)

[Row-level security (RLS)](/en-us/fabric/security/service-admin-row-level-security) might affect the ability of users with read or build permission on a semantic model to read data from the semantic model.

- When RLS **isn't** defined on the semantic model, users with write, read, or build permission on the semantic model can read data from the semantic model.
- When RLS **is** defined on the semantic model:
  - Users with only read or build permission on the semantic model can't read data from the semantic model unless they belong to one of its RLS roles.
  - Users with write permission on the semantic model can read data from the semantic model regardless of whether or not they belong to any of its RLS roles.

## Related content

- [Share access to a semantic model](service-datasets-share)
- [Manage semantic model access permissions](service-datasets-manage-access-permissions)
- [Semantic model REST API permissions](../developer/embedded/datasets-permissions)

---

- Last updated on 
  2026-09-24
