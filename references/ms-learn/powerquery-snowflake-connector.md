Source: https://learn.microsoft.com/power-query/connectors/snowflake
Fetched: 2026-10-23

# Snowflake

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Snowflake

## Summary

| Property | Value |
| --- | --- |
| Connector | Snowflake icon Snowflake |
| Products | Power BI (semantic models) [Power Query Online](/en-us/power-query/power-query-what-is-power-query#power-query-online) |
| Release state | General availability |
| Category | Database |
| [Authentication kinds](/en-us/power-query/connectors/snowflake#authentication-types-supported) | KeyPair Microsoft Account Snowflake |
| Product-specific authentication | Service Principal (Power BI / Fabric) Workspace Identity (Power BI / Fabric) |
| Data source kind | Snowflake |
| Function Reference Documentation | `Snowflake.Databases` |

Note

Some capabilities might be present in one product but not others due to deployment schedules and host-specific capabilities.

Note

The passphrase input field automatically appears only if necessary, based on the type of certificate uploaded. After the user uploads a certificate, the system detects whether it's encrypted or unencrypted and conditionally displays the passphrase dialog. Both encrypted and unencrypted keys are supported.

Important

This connector is transitioning from the embedded Simba Snowflake ODBC driver to the Snowflake ADBC driver. For migration guidance, key dates, and admin controls, see [Transition from ODBC to ADBC drivers in Power BI and Fabric](/en-us/power-query/transition-to-adbc).

## Supported capabilities

- Import
- DirectQuery (Power BI semantic models)
- Advanced options
  - Specify a text value to use as Role name
  - Relationship columns
  - Connection timeout in seconds
  - Command timeout in seconds
  - Database
  - Native SQL statement

## Parameters

**Entry point:** `Snowflake.Databases`

**Required parameter count:** 2

Import data from a Snowflake Computing warehouse.

Returns a table listing the tables in the Snowflake Computing `warehouse` located at `server`. An optional record parameter, `options`, may be specified to control the following options:

- `Role`: A text value to use as the Role name for the connection.
- `CreateNavigationProperties`: A logical (true/false) value that sets whether to generate navigation properties on the returned values (default is true).
- `ConnectionTimeout`: The number of seconds to wait for network responses from Snowflake.
- `CommandTimeout`: The number of seconds to wait for a query to execute.

| Parameter | Display name | Required | Type | Group | Sample values | Nullable |
| --- | --- | --- | --- | --- | --- | --- |
| server | Server | Yes | text |  | "contoso.snowflakecomputing.com" | false |
| warehouse | Warehouse | Yes | text |  | "CONTOSO\_WH" | false |
| options | Advanced Options | No | nullable record | Advanced Options |  | true |

### Fields in `options`

| Field | Display name | Required | Type | Group | Description | Declared default | Allowed values | Sample values | Nullable | Optional | Declared allowed values |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| options.Role | Specify a text value to use as Role name | No | nullable text | Advanced Options |  |  |  | "Enter a text value to use as Role name" | true | true |  |
| options.CreateNavigationProperties | Include relationship columns | No | nullable logical | Advanced Options |  |  |  | true | true | true |  |
| options.ConnectionTimeout | Connection timeout in seconds | No | nullable number | Advanced Options |  |  |  | 60 | true | true |  |
| options.CommandTimeout | Command timeout in seconds | No | nullable number | Advanced Options |  |  |  | 300 | true | true |  |
| options.Implementation | Implementation | No | nullable text | Advanced Options | Use '2.0' to specify ADBC. The 'default' value will use the environment configuration to determine which driver to use. | "2.0" | null (default); "2.0" (2.0) |  | true | true | [null, "2.0"] |

## Connect from Power Query Desktop

Note

All new connections use the [**Snowflake connector implementation 2.0**](/en-us/power-query/connectors/snowflake#snowflake-connector-implementation-20) by default.

We recommend you update any connections created before March 2025 to [this new implementation.](/en-us/power-query/connectors/snowflake#snowflake-connector-implementation-20)

To make the connection to a **Snowflake** computing warehouse, take the following steps:

1. Select **Get Data** from the **Home** ribbon in Power BI Desktop, select **Database** from the categories on the left, select **Snowflake**, and then select **Connect**.

   ![Screenshot of the Get Data dialog, showing the Snowflake database selection.](/en-us/power-query/connectors/media/snowflake/snowflake-get-data.png)
2. In the **Snowflake** window that appears, enter the name of your Snowflake server in **Server** and the name of your Snowflake computing warehouse in **Warehouse**.

   ![Screenshot of the Snowflake dialog, showing the Import radio button selected.](/en-us/power-query/connectors/media/snowflake/snowflake-connection-screen.png)
3. Optionally, enter values in any advanced options that you want to use to modify the connection query, such as a text value to use as a Role name or a command timeout. For more information, go to [Connect using advanced options](/en-us/power-query/connectors/snowflake#connect-using-advanced-options).
4. Select **OK**.
5. To sign in to your Snowflake computing warehouse, enter your username and password, and then select **Connect**.

   ![Screenshot of the Snowflake credential prompt, showing the Username and Password fields.](/en-us/power-query/connectors/media/snowflake/snowflake-authentication.png)

   Note

   Once you enter your username and password for a particular **Snowflake** server, Power BI Desktop uses those same credentials in subsequent connection attempts. You can modify those credentials by going to **File > Options and settings > Data source settings**. For more information, go to [Change the authentication method](/en-us/power-query/connector-authentication#change-the-authentication-method).

   If you want to use the Microsoft account option, the Snowflake Microsoft Entra ID integration must be configured on the Snowflake side. For more information, go to [Power BI SSO to Snowflake - Getting Started](https://docs.snowflake.com/en/user-guide/oauth-powerbi#getting-started).
6. In **Navigator**, select one or multiple elements to import and use in Power BI Desktop. Then select either **Load** to load the table in Power BI Desktop, or **Transform Data** to open the Power Query editor where you can filter and refine the set of data you want to use, and then load that refined set of data into Power BI Desktop.

   ![Screenshot of the Navigator with the test schema database open and the DimProduct table selected.](/en-us/power-query/connectors/media/snowflake/navigator-desktop.png)
7. Select **Import** to import data directly into Power BI, or select **DirectQuery**, then select **OK**. For more information, go to [Use DirectQuery in Power BI Desktop](/en-us/power-bi/connect-data/desktop-use-directquery).

   Note

   Microsoft Entra ID single sign-on (SSO) only supports DirectQuery.

   ![Screenshot of Connection settings, which contains the Import and DirectQuery selections.](/en-us/power-query/connectors/media/snowflake/connection-settings-desktop.png)

## Connect from Power Query Online

To make the connection, take the following steps:

1. Select the **Snowflake** option in the connector selection.
2. In the **Snowflake** dialog that appears, enter the name of the server and warehouse.

   ![Screenshot of the Snowflake connection builder in Power Query Online.](/en-us/power-query/connectors/media/snowflake/snowflake-pqo-advanced.png)
3. Enter any values in the advanced options you want to use. If there are any advanced options not represented in the UI, you can edit them in the **Advanced Editor** in Power Query later.
4. Enter your connection credentials, including selecting or creating a new connection, which gateway you would like to use, and a username and password.
5. Select **Next** to connect to the database.
6. In **Navigator**, select the data you require, then select **Transform data** to transform the data in Power Query Editor.

   ![Screenshot of the online Navigator with the test schema database open and the DimProduct table selected.](/en-us/power-query/connectors/media/snowflake/navigator-online.png)

## Additional information

### Authentication details

Note

- Username/password authentication mode will be deprecated. [Read more here](https://www.snowflake.com/en/blog/blocking-single-factor-password-authentification/). More information can be found under Connectivity on our [Fabric roadmap](https://roadmap.fabric.microsoft.com/?product=datafactory).
- Key Pair Auth isn't supported for Dataflows Gen1 and Power Apps (Dataflows).

The Snowflake connector supports the following authentication methods:

- **Microsoft Entra ID (recommended)**: Enables strong, identity-based authentication without storing usernames or passwords.

  - In **Microsoft Fabric**, this authentication method can be backed by **workspace identity** in supported experiences (such as **Datasets** and **Dataflows Gen2**), allowing Fabric to authenticate to Snowflake using the workspaceâs managed identity.
- **Workspace Identity**: A managed identity associated with a Microsoft Fabric workspace. When you authenticate with Microsoft Entra ID, supported Fabric experiences (such as Datasets and Dataflows Gen2) can use the workspace identity to authenticate to Snowflake. This method allows Fabric to access Snowflake using an identity tied to the workspace, rather than individual user credentials.
- **Key pair authentication (ADBC)**: Certificate-based authentication for supported scenarios.
- **Service Principal (SPN)**: Service principals are supported with Snowflake for scenarios where a non-user, application-level identity is required. Support is dependent on Snowflake configuration and the authentication method used.

### Advanced options

Power Query provides a set of advanced options that you can add to your query if needed.

The following table lists all of the advanced options you can set in Power Query.

| Advanced option | Description |
| --- | --- |
| Role name | Specifies the role that the report uses via the driver. This role must be available to the user. Otherwise no role is set. |
| Include relationship columns | If checked, includes columns that might have relationships to other tables. If this box is cleared, you donât see those columns. |
| Connection timeout in seconds | Specifies how long to wait for a response when interacting with the Snowflake service before returning an error. Default is 0 (no timeout). |
| Command timeout in seconds | Specifies how long to wait for a query to complete before returning an error. Default is 0 (no timeout). |
| Database | Specifies a specific database in the warehouse. This option is only available in Power Query Desktop. |
| SQL Statement | For information, see [Import data from a database using native database query](/en-us/power-query/native-database-query). |

Once you select the advanced options you require, select **OK** in Power Query Desktop or **Next** in Power Query Online to connect to your Snowflake database.

### Implementation 2.0

In January 2025, we introduced a new implementation for the Snowflake connector to enhance the integration with Snowflake. This connector is generally available since July 2025. We recommend that you upgrade Power BI Desktop and the on-premises data gateway to the latest version to benefit from the most current capabilities. [Provide us feedback](https://aka.ms/snowflake-connector-feedback) to help us continue improving the connector.

The Snowflake connector implementation 2.0 is built using the open-source [Arrow Database Connectivity](https://arrow.apache.org/docs/format/ADBC.html) (ADBC) driver. ADBC provides a set of standard interfaces for interacting with Arrow data, which is especially efficient at fetching large datasets with minimal overhead and no serialization or copying. The ADBC driver also incorporates security enhancements, such as memory safety and garbage collection. Additionally, collaboration with the open-source community enables more rapid updates, utilizing modern tools and secure development lifecycle (SDL) processes.

To enable you to take advantage of these performance and security enhancements, starting July 2025, all the newly created connections in Desktop automatically use the 2.0 implementation. You can also test the 2.0 implementation by updating your existing queries and adding the `Implementation="2.0"` flag in `Snowflake.Databases` as follows.

```
Source = Snowflake.Databases("contoso.snowflakecomputing.com", "CONTOSO_WH", [Implementation="2.0"])
```

To aid with diagnosing any potential issue, you can find the `Implementation` and `DriverType` details in your Mashup logs like the following example. If you encounter any issue during the transition, contact support. Meanwhile, to self-mitigate, you can remove `Implementation="2.0"` to keep using the ODBC connector to avoid business interruption before the issue is resolved. However, if you're using Key Pair authentication, the ADBC driver is always used regardless of this setting.

```
{
   "Start":"2024-11-02T00:14:02.7968686Z",
   "Action":"Engine/Module/Snowflake/IO/Snowflake/Implementation",
   "ResourceKind":"Snowflake",
   "ResourcePath":"powerbi.snowflakecomputing.com ;DEMO_WH",
   "HostProcessId":"29200",
   "Implementation":"2.0",
   "DriverType":"ADBC",
   "ProductVersion":"2.139.0.0 (Main)+eda56ecd858054173a4d11db9c63a6da5cf92a99",
   "ActivityId":"106f16b6-cfbb-4853-9f20-ed45486486d2",
   "Process":"Microsoft.Mashup.Container.NetFX45",
   "Pid":38560,
   "Tid":1,
   "Duration":"00:00:00.0000291"
}
```

The following options are available since the July 2025 release:

- `UseHighPrecision`: Controls the precision of how Snowflake NUMBER(38,0) fields should be handled. If no value is specified, the connector queries Snowflake using the `SHOW PARAMETERS LIKE 'ODBC_TREAT_DECIMAL_AS_INT'` query. If the no value is set, then the connector uses the scale specified by the column. A `true` value treats NUMBER(38,0) as a Decimal type. The value `false` treats NUMBER(38,0) as an Int64 type. If the scale is higher than 0, then the column is considered as a Double type.
- `DateTimePrecision`: Controls the precision of how Snowflake Timestamp values are treated. Snowflake typically stores Timestamp values with nanosecond precision. In ADBC, this precision can cause an overflow exception for dates before 1677 or after 2262, [according to Snowflake](https://pkg.go.dev/github.com/snowflakedb/gosnowflake#hdr-Arrow_batches). Valid values for this option are *null*, `nanoseconds`, or `microseconds`. A *null* value uses `microseconds` by default. We recommend that users who need dates before 1677 or after 2262 use the `microseconds` setting. If users need to retain precision to the ten millionth place before 1677 or after 2262, we recommend staying with the ODBC driver.

If you need to use proxy to connect to Snowflake, refer to the [proxy setting instruction](https://pkg.go.dev/github.com/snowflakedb/gosnowflake#hdr-Proxy). The driver uses environment variables for the proxy settings.

Note

When you use the on-premises data gateway, note the minimal supported version is January 2025. We recommend you use the latest version with the most current capabilities.

Note

This feature is supported in the 64-bit version of Power BI Desktop and doesn't work in the 32-bit version.

## Limitations and considerations

### Known issues in Snowflake connector implementation 2.0

Currently, the [Snowflake connector implementation 2.0](/en-us/power-query/connectors/snowflake#snowflake-connector-implementation-20) has the following known issues. There's ongoing work towards a fix and the documentation will be updated when a fix is released.

- Snowflake query with `count distinct` logic returns incorrect result.
- Increased memory use. The overall load time is typically faster using `Implementation="2.0"`, but the memory consumption can also be higher, in some cases causing issues such as `Resource Governing: This operation was canceled because there wasn't enough memory to finish running it. Either reduce the memory footprint of your dataset by doing things such as limiting the amount of imported data, or if using Power BI Premium, increase the memory of the Premium capacity where this dataset is hosted.`

### Resolved issues

#### Hyphens in database names

If a database name has a hyphen in it, you can encounter an `ODBC: ERROR[42000] SQL compilation error`. This issue is addressed in the September 2024 release.

#### Slicer visual for Boolean datatype

The slicer visual for the Boolean data type isn't functioning as expected in the June 2024 release. This nonfunctionality is a known issue. As a temporary solution, users can convert the Boolean data type in their reports to text by navigating to: Transfer -> Data Type -> Text. A fix is provided in October 2024 release.

#### Views not visible with Implementation="2.0"

In some version of the March 2025 release of Power BI Desktop, you might encounter an issue that views aren't visible when using the [Snowflake connector implementation 2.0](/en-us/power-query/connectors/snowflake#snowflake-connector-implementation-20) (`Implementation="2.0"`). This issue is fixed since the latest March 2025 release of Power BI Desktop. To try again, upgrade your installation.

## Troubleshooting

### Error: SQL compilation error: Object does not exist, or operation cannot be performed

The error occurs when the system can't find the specified object. Often, this error is due to the user having an invalid database name set as their default database.

Ensure that a valid default database name is used for the property DEFAULT\_NAMESPACE:
`DESC USER`*`username`*

To update the default database name: `alter user`*`username`* `set DEFAULT_NAMESPACE=<database name>.<schema name>`. For more information, go to the [Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/alter-user).

## Release history

The following table contains a summary of the connector enhancements released in past versions:

| Release | Connector improvement |
| --- | --- |
| July 2025 | â¢ Boolean columns return Boolean types, fixing the issue where Boolean columns were treated as String types in an empty record set schema (including metadata). â¢ New setting to set the maximum timestamp precision to microseconds. â¢ Improved Duration support. â¢ Added support for navigation properties to ADBC. â¢ Improved tracing in the ADBC driver, where the âActivityId" can now be traced through the driver layer. |
| April 2025 | â¢ Added support for Snowflake query tag. As an example: `{"PowerQuery":true,"Host":"PBI_SemanticModel_MWC","HostContext":"PowerBIPremium-DirectQuery"}` |
| March 2025 | â¢ Enhanced performance when retrieving data from Snowflake. â¢ Enabled by default in Power BI Desktop so that the newly created connections automatically use the new connector implementation. â¢ Fixed the [views not visible issue](/en-us/power-query/connectors/snowflake#views-not-visible-with-implementation20) since the latest March release. |
| February 2025 | â¢ Enhanced performance by reducing the number of metadata calls. â¢ Resolved duplicate values issue for large result sets. |

## Related content

- [Connect to Snowflake in Power BI Service](/en-us/power-bi/connect-data/service-connect-snowflake)

---

- Last updated on 
  2026-10-09
