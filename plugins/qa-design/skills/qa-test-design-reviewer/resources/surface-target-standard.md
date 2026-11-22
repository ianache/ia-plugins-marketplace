# Surface Target — identificación del elemento bajo prueba

Cada TC declara `surface` y `surface_target_id` en frontmatter, tabla de identificación general y detalles específicos. No inventar valores faltantes.

| Surface | Atributos obligatorios |
|---|---|
| API | api_id, base_url_or_service, http_method, endpoint_path, operation_id, request_contract, auth_scheme, response_contract |
| WEB | application_id, component_id, route_or_url, navigation_path, user_role, interaction_control, ui_state |
| MOBILE | application_id, platform, app_version, screen_id, navigation_path, user_role, interaction_control |
| DATABASE | datastore_id, schema, table_or_view, operation_or_query, transaction_context, data_scope |
| EVENT | broker_or_bus, topic_or_queue, event_type, schema_id_version, producer, consumer, correlation_key |
| BATCH | job_id, scheduler_or_trigger, entrypoint, input_dataset, output_artifact, execution_parameters |
| INTEGRATION | source_system, target_system, interface_id, protocol, operation_or_message, correlation_id |
| CROSS_SURFACE | journey_id, ordered_targets, entry_surface, exit_surface, correlation_id, end_to_end_oracle |

Los targets CROSS_SURFACE deben incluir secuencia de targets individuales. No publicar credenciales reales. La revisión humana verifica existencia, accesibilidad y versión del target.
