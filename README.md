# Netgear Exporter

A Prometheus exporter for the Netgear GS108Ev3 managed switch. This switch does
not have any API / automation interface, so this exporter retrieves the HTML
pages from the switch UI and parses them to extract switch information and port
status and statistics and publishes them in [Prometheus](https://prometheus.io)
format.

License: [MIT](./LICENSE.md)
