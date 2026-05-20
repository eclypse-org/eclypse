graph [
  directed 1
  node_default [
  ]
  edge_default [
  ]
  scenario "io-round-trip"
  source_format "graphml"
  id "infrastructure"
  node [
    id 0
    label "cloud"
    cpu 64.0
    ram 128.0
    storage 2048.0
    gpu 32
    availability 0.999
    processing_time 5
    tier "cloud"
  ]
  node [
    id 1
    label "edge-a"
    cpu 16.0
    ram 32.0
    storage 512.0
    gpu 128
    availability 0.995
    processing_time 3
    tier "edge"
  ]
  node [
    id 2
    label "edge-b"
    cpu 12.0
    ram 24.0
    storage 256.0
    gpu 2
    availability 0.99
    processing_time 23
    tier "edge"
  ]
  edge [
    source 1
    target 0
    latency 18.0
    bandwidth 500.0
    link_type "wan"
  ]
  edge [
    source 1
    target 2
    latency 4.0
    bandwidth 1000.0
    link_type "lan"
  ]
  edge [
    source 2
    target 0
    latency 22.0
    bandwidth 450.0
    link_type "wan"
  ]
]
