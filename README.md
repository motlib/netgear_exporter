# Netgear Exporter

License: [MIT](./LICENSE.md)

A [Prometheus](https://prometheus.io) exporter for the Netgear GS108Ev3 managed
switch. This switch does not have any documented API / automation interface
(apart from NSDP), so this exporter retrieves the HTML pages from the switch UI
and parses them to extract switch information and port status and statistics and
publishes them in Prometheus format.

Here you can find an example of the generated metrics output:
[metrics example](./docs/metrics_example.txt).

## Usage

For testing, you can run the exporter as a Docker container like this, replacing
`MY_PASSWORD` with the login password of the switch.

```sh
docker run \
  --rm \
  --interactive --tty \
  --env 'NETGEAR_EXPORTER_AUTH_MODULES={"default":"MY_PASSWORD"}' \
  --publish 8177:8177 \
  --name netgear_exporter \
  motlib/netgear_exporter:latest
```

Then point your browser to the following URL to retrieve the Prometheus metrics:

http://localhost:8177/probe?target=192.168.0.239&auth_module=default

You need to take care to replace the IP address `192.168.0.239` with the actual
IP address of your switch.

This URL follows the Prometheus
[multi-target exporter](https://prometheus.io/docs/guides/multi-target-exporter/)
pattern.

## Prometheus Configuration

This is a simple configuration snippet for the Prometheus configuration (usually
 `prometheus.yml`):

```yaml
scrape_configs:
  - job_name: netgear
    scrape_interval: 60s
    metrics_path: /probe
    static_configs:
      - targets:
        # This is the list of switch IP addresses to monitor.
        - '192.168.0.239'
    params:
      # The auth module (i.e. password) configured to connect to the switches
      # listed above.
      auth_module: [default]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        # The netgear exporter's hostname:port
        replacement: npi3:8177
```

