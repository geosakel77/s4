from s4lib.apisrv.libapiserver import APIServerCoordinator

if __name__ == "__main__":
    coordinator = APIServerCoordinator("COORD")
    print(coordinator.agent_uuid)

    coordinator.run()
