job "oswe-clusterHelloWorld-PLACEHOLDER_COMMIT" {

  datacenters = ["cluster"]
  type = "batch"

  group "training-task-group" {

    task "training-main" {
      leader = true
      driver = "docker"
      config {
        image = "registry.fme.lan/cluster_hello_world/oswe-clusterhelloworld:latest"

        command = "/prep/_setupAndRunInsideDocker.sh"
        args = ["PLACEHOLDER_COMMIT"]
        volumes = [
          "/deep_learning/input/data/oswe-clusterhelloworld:/input:ro",
          "/deep_learning/output/oswe-clusterhelloworld:/output",
          "/var/lib/nvcache:/root/.nv"
        ]
      }

      resources {
        cpu = 1000
        memory = 256
        network {
          mbits = 100
        }
        # not needed here
        # device "nvidia/gpu" {
        #   count = 1
        # }
      }
    }

    restart {
      attempts = 0
      mode = "fail"
    }
  }
}
