# Import and Export

ECLYPSE provides an import/export layer for moving
[Infrastructure][eclypse.graph.infrastructure.Infrastructure] and
[Application][eclypse.graph.application.Application] objects between simulations,
external tools, and standard infrastructure descriptions.

The IO package is intentionally separated from reporting. Reporters persist data
produced *during* a simulation. Importers and exporters persist the graph objects
that are needed *to build* a simulation.

## Basic usage

The public API exposes specialised functions for applications and
infrastructures:

=== "Application"

    ```python
    from eclypse.io import dump_application, load_application

    dump_application(application, "application.json")
    loaded = load_application("application.json")
    ```

=== "Infrastructure"

    ```python
    from eclypse.io import dump_infrastructure, load_infrastructure

    dump_infrastructure(infrastructure, "infrastructure.graphml")
    loaded = load_infrastructure("infrastructure.graphml")
    ```

In most cases, ECLYPSE infers the format from the file extension. You can also
select a format explicitly with the `using` argument:

```python
dump_application(application, "application.yaml", using="docker-compose")
application = load_application("application.yaml", using="docker-compose")

dump_infrastructure(infrastructure, "infrastructure.yaml", using="tosca")
infrastructure = load_infrastructure("infrastructure.yaml", using="tosca")
```

## Supported formats

The built-in [eclypse.io.defaults][eclypse.io.defaults] registry provides default importers and
exporters for common graph and cloud-edge formats.

| Format | Application | Infrastructure | Main use |
| --- | --- | --- | --- |
| [`eclypse-json`][eclypse.io.defaults.json] | :octicons-check-16: | :octicons-check-16: | Lossless ECLYPSE round-trip through [JSONImporter][eclypse.io.defaults.json.JSONImporter] and [JSONExporter][eclypse.io.defaults.json.JSONExporter]. |
| [`node-link-json`][eclypse.io.defaults.node_link] | :octicons-check-16: | :octicons-check-16: | Portable NetworkX-style graph data. |
| [`gml`][eclypse.io.defaults.gml] | :octicons-check-16: | :octicons-check-16: | Graph exchange with simple attributes. |
| [`graphml`][eclypse.io.defaults.graphml] | :octicons-check-16: | :octicons-check-16: | Graph exchange with XML-based tooling. |
| [`docker-compose`][eclypse.io.defaults.docker_compose] | :octicons-check-16: | :octicons-x-16: | Import or export service-level applications. |
| [`tosca`][eclypse.io.defaults.tosca] | :octicons-check-16: | :octicons-check-16: | Import or export cloud/service topology templates. |

[`eclypse-json`][eclypse.io.defaults.json] is the canonical ECLYPSE format.
It stores the graph kind, identifier, graph attributes, node and edge assets,
nodes, edges, and kind-specific metadata such as application flows or
infrastructure path aggregators.

Graph formats such as GML, GraphML, and node-link JSON focus on topology and
serialisable graph attributes. They are useful for interoperability, but they do
not carry the complete ECLYPSE model in the same way as
[`eclypse-json`][eclypse.io.defaults.json].

## Docker Compose

Docker Compose files are imported as
[Application][eclypse.graph.application.Application] objects.

```yaml title="docker-compose.yaml"
name: video-pipeline

services:
  camera:
    image: camera-gateway:latest

  inference:
    image: inference-service:latest
    depends_on:
      - camera
```

When loaded, each service becomes an application node. The service `image` is
stored as a node attribute, and Docker Compose `depends_on` becomes a
directed interaction:

```python
from eclypse.io import load_application

application = load_application("docker-compose.yaml", using="docker-compose")

application.nodes["camera"]["image"]
# "camera-gateway:latest"

list(application.edges)
# [("inference", "camera")]
```

When exporting to Docker Compose, each application node must define either an
`image`, a `container_image`, or a `build` attribute. This mirrors the
operational nature of Docker Compose: ECLYPSE does not silently invent container
images by default.

```python
application.add_node("frontend", image="nginx:latest", strict=False)
dump_application(application, "docker-compose.yaml", using="docker-compose")
```

If you explicitly want to use the node identifier as a fallback image, pass a
[DockerComposeContext][eclypse.io.context.DockerComposeContext]:

```python
from eclypse.io import DockerComposeContext

dump_application(
    application,
    "docker-compose.yaml",
    using="docker-compose",
    application_context=DockerComposeContext(allow_image_fallback_to_node=True),
)
```

ECLYPSE writes optional `x-eclypse` extension fields to preserve metadata such
as graph attributes, flows, and edge attributes. These fields are standard
Compose extension fields and are ignored by Docker Compose implementations that
do not understand them.

## TOSCA

TOSCA files are exported using standard TOSCA Simple Profile YAML types.
ECLYPSE-specific metadata is stored only under optional `x-eclypse` extension
fields.

Applications are represented as software components with dependency
requirements:

```yaml title="application.tosca.yaml"
tosca_definitions_version: tosca_simple_yaml_1_3
metadata:
  template_name: app
topology_template:
  node_templates:
    frontend:
      type: tosca.nodes.SoftwareComponent
      requirements:
        - dependency:
            node: worker
            relationship: tosca.relationships.DependsOn
    worker:
      type: tosca.nodes.SoftwareComponent
```

Infrastructures are represented with TOSCA compute, network, and port node
templates:

```yaml title="infrastructure.tosca.yaml"
tosca_definitions_version: tosca_simple_yaml_1_3
metadata:
  template_name: infra
topology_template:
  node_templates:
    node_a:
      type: tosca.nodes.Compute
      capabilities:
        host:
          properties:
            num_cpus: 4
            mem_size: 8 GB
    private_net:
      type: tosca.nodes.network.Network
    port_a:
      type: tosca.nodes.network.Port
      requirements:
        - binding:
            node: node_a
            relationship: tosca.relationships.HostedOn
        - link:
            node: private_net
            relationship: tosca.relationships.network.LinksTo
```

By default, [TOSCAImporter][eclypse.io.defaults.tosca.TOSCAImporter] validates fields
required by the service template: `tosca_definitions_version` must be present,
and each node template must define a `type`.

## Contexts

Contexts customise import and export without changing the graph classes. Common
options live in [IOContext][eclypse.io.context.IOContext]; application and
infrastructure-specific options live in specialised contexts.

| Context | Purpose |
| --- | --- |
| [ApplicationContext][eclypse.io.context.ApplicationContext] | Application import/export defaults, including services and requirement initialisation. |
| [InfrastructureContext][eclypse.io.context.InfrastructureContext] | Infrastructure import/export defaults, including resource initialisation and path aggregators. |
| [DockerComposeContext][eclypse.io.context.DockerComposeContext] | Docker Compose validation and image/build fallback behaviour. |
| [TOSCAApplicationContext][eclypse.io.context.TOSCAApplicationContext] | TOSCA validation options for applications. |
| [TOSCAInfrastructureContext][eclypse.io.context.TOSCAInfrastructureContext] | TOSCA validation options for infrastructures. |

For example, a TOSCA file without the mandatory version can be accepted only by
making that choice explicit:

```python
from eclypse.io import TOSCAApplicationContext, load_application

application = load_application(
    "legacy.yaml",
    using="tosca",
    application_context=TOSCAApplicationContext(
        require_definitions_version=False,
    ),
)
```

## Custom importers and exporters

Importers and exporters are regular classes based on abstract base classes:

- [GraphImporter][eclypse.io.base.GraphImporter]
- [GraphExporter][eclypse.io.base.GraphExporter]

An exporter converts a graph to an intermediate representation and writes it to
a target. An importer reads a source into an intermediate representation and
builds a graph from it.

```python
from eclypse.io import GraphExporter

class MyApplicationExporter(GraphExporter):
    def to_data(self, graph, *, context=None):
        return {"nodes": list(graph.nodes)}

    def write_data(self, data, target, *, context=None):
        ...
```

You can pass custom classes directly, without registering them globally:

```python
dump_application(application, "application.myfmt", using=MyApplicationExporter)
```

If you want reusable names, create or extend an
[IORegistry][eclypse.io.registry.IORegistry]. Registries are immutable: methods such
as [with_exporter][eclypse.io.registry.IORegistry.with_exporter] return a new
registry instead of changing the existing one. The default registry stores
handler classes rather than handler instances, so importers and exporters are
created only when they are used.

```python
from eclypse.io import IORegistry, dump_application

registry = IORegistry().with_exporter(
    "application",
    "my-format",
    MyApplicationExporter,
)

dump_application(
    application,
    "application.myfmt",
    using="my-format",
    registry=registry,
)
```

!!! tip

    Use [`eclypse-json`][eclypse.io.defaults.json] when you need a complete
    ECLYPSE round-trip. Use Docker Compose, TOSCA, GraphML, GML, or node-link
    JSON when interoperability with external tools matters more than preserving
    every simulator-specific detail.
