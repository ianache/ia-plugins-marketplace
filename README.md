# skillcatalog


## Marketplace de Claude Code

El repositorio es un marketplace de plugins de Claude Code: el catálogo está en [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) y cada plugin vive en `plugins/<nombre>/` con su propio `.claude-plugin/plugin.json`.

```text
/plugin marketplace add https://github.com/ianache/ia-plugins-marketplace.git
/plugin install requirements-engineering@ia-plugins-marketplace
```

Equivalente en terminal: `claude plugin marketplace add <URL>` y `claude plugin install <plugin>@comsatel-skills-catalog`. El repositorio es privado: Git debe tener credenciales para `project.comsatel.com.pe`.

Al agregar un plugin nuevo a `plugins/`, añada su entrada en `marketplace.json` (`name` igual al de su `plugin.json` y `source` `./plugins/<nombre>`) y valide con `claude plugin validate .`. La versión se mantiene solo en el `plugin.json` de cada plugin.

## Marketplace de Codex

El mismo repositorio también ofrece un catálogo para Codex en [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json). Sus entradas usan el formato de marketplace de Codex y apuntan a los mismos paquetes de `plugins/`, que contienen `skills/` y manifiestos compatibles con Claude.

```text
codex plugin marketplace add https://github.com/ianache/ia-plugins-marketplace.git --sparse .agents/plugins --sparse plugins
```

En Codex, abra el directorio de plugins con `/plugins` y seleccione `COMSATEL Skills Catalog`. Para cada plugin nuevo, mantenga su manifiesto y skills en `plugins/<nombre>/` y agregue una entrada equivalente en ambos catálogos: `.claude-plugin/marketplace.json` y `.agents/plugins/marketplace.json`.
