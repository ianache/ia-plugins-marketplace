# Fact and Dimension Modelling Standard

**Version:** 1.0.0
**Applies to:** `bi-analytics`, task T-04 / gate G4, artifact DMD
**Normative terms:** MUST, SHOULD and MAY express requirements for this plugin.

## 1. Purpose and scope

This standard defines logical naming and design documentation for dimensional models produced by `bi-dimensional-model-designer`. It applies to fact tables, dimensions, columns, keys, constraints, indexes, bridges, views and partitions when those objects are in scope.

The `fact_` and `dim_` prefixes below are COMSATEL conventions for this plugin, not universal requirements of dimensional modeling. The design principles follow established dimensional modeling practice: state the fact grain first, keep a uniform grain per fact, use dimension surrogate keys, and preserve referential integrity. Physical syntax and optimization remain platform-specific and MUST be identified as decisions or open items in the DMD.

This is a logical modeling standard. It does not authorize the skill to produce DDL, ETL code, or vendor-specific index/partition definitions.

## 2. Identifier format

1. Use lowercase `snake_case`, ASCII letters, digits and underscores. Names MUST start with a letter, MUST NOT contain spaces, quoted identifiers, accents, or reserved words, and SHOULD remain within the target platform's identifier limit.
2. Prefer clear business nouns and terms from the approved glossary. Avoid unexplained abbreviations, generic names such as `name`, `type`, `value`, `key` or `date`, and redundant qualifiers.
3. Use singular entity nouns for dimensions (`dim_customer`, `dim_product`). Name a fact for its measured process and grain (`fact_sales_line`, `fact_inventory_daily_snapshot`); the name and its documented grain MUST agree.
4. Names are stable interfaces. In EVOLUTION, preserve existing names unless the change is approved and its impact is documented. For BROWNFIELD, record existing nonconforming names and distinguish them from proposed names; do not silently rename them.

## 3. Table patterns

| Object | Convention | Example |
|---|---|---|
| Transaction/event fact | `fact_<process_or_event>[_<grain>]` | `fact_sales_line` |
| Periodic snapshot fact | `fact_<subject>_<period>_snapshot` | `fact_inventory_daily_snapshot` |
| Accumulating snapshot fact | `fact_<process>_lifecycle` or `fact_<process>_milestone` | `fact_order_lifecycle` |
| Factless fact | `fact_<event_or_coverage>` | `fact_attendance` |
| Dimension | `dim_<business_entity>` | `dim_customer` |
| Bridge for multivalued relationship | `bridge_<entity_a>_<entity_b>` | `bridge_account_contact` |
| Aggregate fact | `fact_<process>_<aggregation_grain>` | `fact_sales_monthly` |
| Logical view | `vw_<subject>` | `vw_sales_performance` |
| Materialized view, if supported | `mv_<subject>` | `mv_sales_monthly` |

Do not introduce a new table prefix when an applicable pattern exists. A bridge MUST document the relationship grain and any allocation rule. Aggregate facts MUST identify their source/atomic fact and aggregation grain. Keep staging, raw, and operational objects outside this standard unless the DMD explicitly includes them.

## 4. Column names and keys

### 4.1 Dimension columns

- Every dimension has one single-column primary key named `<dimension_entity>_key`, e.g. `customer_key` in `dim_customer`. It SHOULD be a meaningless surrogate distinct from source/business identifiers. `dim_date` MAY use a chronological integer key named `date_key` (commonly `YYYYMMDD`) when this is an explicit, consistent warehouse convention; it MUST NOT be confused with a source-system natural key.
- Source/business identifiers use `<entity>_id` or the approved source term, e.g. `customer_id`. If multiple source systems can issue the same identifier, include the source identity (`source_system_code`) or define a documented composite business key. Never use a source natural key as the dimensional surrogate key.
- Descriptive attributes use meaningful business names, e.g. `customer_name`, `customer_segment_code`, `customer_segment_name`; do not repeat `customer_` on every attribute when the dimension context already makes it redundant, unless needed for clarity or conformance.
- Role-playing date dimensions use one conformed `dim_date` and role-specific fact foreign keys such as `order_date_key`, `ship_date_key`, and `delivery_date_key`.

### 4.2 Fact columns

- Each dimension foreign key in a fact MUST use the corresponding role/entity name plus `_key`, e.g. `customer_key`, `product_key`, `order_date_key`; it MUST reference the dimension surrogate key and respect the declared grain.
- Degenerate identifiers retained in the fact use business names such as `order_number` or `invoice_number`; identify them as degenerate dimensions in the DMD.
- Name measures as business quantities, e.g. `sales_amount`, `units_sold_quantity`, `discount_amount`, `order_count`. Include unit/currency where ambiguity is possible (`local_currency_amount`, `usd_amount`) and document additivity. Ratios and percentages SHOULD be calculated from their numerator and denominator; if stored, use a clear suffix such as `_rate` or `_percent` and declare non-additivity.
- A fact table MUST NOT contain descriptive attributes that belong in a dimension, except documented degenerate dimensions or other justified dimensional patterns.

### 4.3 SCD and audit columns

For SCD Type 2 dimensions, use `effective_start_at`, `effective_end_at`, and `is_current` (boolean) unless the platform or enterprise standard requires established alternatives. Document inclusive/exclusive boundary semantics and the unknown/not-applicable member strategy. Use consistent audit names such as `created_at`, `updated_at`, `source_system_code`, and `load_batch_id` only when required by the platform/governance contract; do not add them mechanically to every model.

## 5. Constraints and other objects

| Object | Convention | Example |
|---|---|---|
| Primary key constraint | `pk_<table>` | `pk_dim_customer` |
| Foreign key constraint | `fk_<fact>_<dimension>[_<role>]` | `fk_fact_sales_line_dim_customer` |
| Unique constraint | `uq_<table>_<business_key>` | `uq_dim_customer_source_customer_id` |
| Check constraint | `ck_<table>_<rule>` | `ck_dim_date_month_number` |
| Default constraint, when named by platform | `df_<table>_<column>` | `df_fact_sales_line_is_return` |
| Non-unique index | `ix_<table>_<ordered_columns>` | `ix_fact_sales_line_order_date_customer` |
| Unique index (only if not represented by a unique constraint) | `ux_<table>_<ordered_columns>` | `ux_dim_customer_source_customer_id` |
| Sequence, when required by platform | `seq_<table>_<purpose>` | `seq_dim_customer_key` |
| Partition | `p_<table>_<period_or_range>` | `p_fact_sales_line_2026_01` |

Constraint/index names MUST be unique within the platform's namespace and shortened consistently when identifier limits require it. Do not model both a unique constraint and a duplicate unique index for the same rule. The DMD MUST name candidate PK, FK and business-key uniqueness rules; it SHOULD identify index candidates only where justified by access patterns, relationship cardinality, partitioning, or platform guidance.

Do not prescribe an index for every column or foreign key. Evaluate indexes against expected filters/joins, table size, write/load cost, storage engine, and native columnar/clustered/partitioning features. The physical index type, order, included columns, clustering, and partition syntax are platform-specific and MUST be marked `TBD` with the decision owner when the platform is unknown.

## 6. Model documentation required in DMD

For every proposed fact and dimension, document:

- canonical table name, object pattern, business process/entity, and lifecycle action (`CREATE`, `UPDATE`, `NO_CHANGE`, or `BLOCKED`);
- fact grain, dimensions and their roles, measures, additivity, and KPI lineage;
- each column's name, role (PK, FK, business key, degenerate dimension, measure, descriptive, SCD/audit), business definition, source, and nullability expectation when known;
- dimension surrogate key and natural/business key; SCD behavior and effective-date columns where applicable;
- PK/FK/unique/check rules and index/partition candidates with rationale, or `TBD` and an owner where platform facts are unknown;
- exceptions for inherited Brownfield names and approved Evolution renames, with impact and compatibility notes.

The Mermaid model MUST use the canonical `fact_` and `dim_` names and show each relationship's cardinality where supported. This is a design specification, not executable DDL.

## 7. Validation checklist

- [ ] Every fact uses `fact_`, every dimension uses `dim_`, and every table name agrees with its documented business process/entity and grain.
- [ ] Each fact has one explicit, uniform grain; dimensions and measures are valid at that grain.
- [ ] Each dimension has one surrogate `<entity>_key`; fact FKs use matching role-specific `_key` names.
- [ ] Natural/source IDs are distinct from surrogate keys; source identity is handled where needed.
- [ ] Measures have business-specific names, units/currency where needed, and additivity documented.
- [ ] SCD, unknown/not-applicable members, bridges, and degenerate dimensions are named and explained where used.
- [ ] Constraints and index candidates follow the patterns and are justified; platform-specific choices are marked `TBD` when unresolved.
- [ ] Mermaid diagram and all DMD tables use the same canonical identifiers.
- [ ] Brownfield deviations and Evolution renames preserve traceability and record impact.

## 8. Basis

- Kimball Group, [Fact Table Structure](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/fact-table-structure/) and [Dimension Table Structure](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/dimension-table-structure/).
- Kimball Group, [Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) (grain, surrogate keys, conformed dimensions, and fact structures).
- Table/column prefixes and object-name patterns in this document are the plugin's local naming policy; dimensional modeling sources establish the roles and behavior of facts, dimensions, keys, and grain, but do not mandate one universal identifier syntax.